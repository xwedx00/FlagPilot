# FlagPilot Backend v7.0 - Deep Technical PRD
**Status**: Reverse-Engineered & Verified
**Date**: Dec 28, 2025

## 1. System Internals & Orchestration Logic

### 1.1 Agent Orchestration (LangGraph)
The core of the system is the **FlagPilot Orchestrator** (`agents/orchestrator.py`), a specialized LangGraph workflow designed for multi-agent delegation.

**State Schema (`OrchestratorState`):**
```python
class OrchestratorState(TypedDict):
    task: str                 # Original user request
    context: Dict[str, Any]   # RAG + Memory context
    selected_agents: List[str]# Agents chosen by Router
    agent_outputs: Dict       # Results from parallel execution
    risk_level: str           # "LOW" | "HIGH" | "CRITICAL"
    is_critical_risk: bool    # Fast-fail safety flag
    final_synthesis: str      # Final LLM-generated response
    status: str               # "executing" | "risk_check" | "synthesizing"
```

**Execution Flow:**
1.  **Planning Node (`plan_node`)**:
    *   **Fast-Fail Scam Check**: Runs `detect_scam_signals()` using keyword analysis (e.g., "telegram", "send check"). If detected -> Immediately marks as critical risk, selects `risk-advisor` ONLY.
    *   **Context Injection**:
        *   **RAG**: Retrieves top 3 chunks (k=3) from Qdrant via `get_rag_pipeline()`.
        *   **Memory**: Fetches user profile summary and global wisdom insights from Elasticsearch.
    *   **Intelligent Routing**: Calls `llm_route_agents` (`agents/router.py`) to select up to 4 agents. Uses an LLM (Temperature 0.1) to analyze the task against detailed agent descriptions.

2.  **Execution Node (`execute_node`)**:
    *   Runs selected agents **concurrently** using `asyncio.gather`.
    *   Each agent inherits from `FlagPilotAgent` (`agents/agents.py`) which wraps a persistent `create_react_agent`.
    *   **Critical Risk Escalation**: If any agent output contains "CRITICAL" and "SCAM"/"FRAUD", the global state escalates to `is_critical_risk=True`.

3.  **Synthesis Node (`synthesize_node`)**:
    *   If `is_critical_risk`: Generates a hard warning block.
    *   Normal: Uses LLM (Temperature 0.3) to synthesize individual agent outputs into a cohesive Markdown report with "Key Findings" and "Recommended Actions".

### 1.2 Authentication & Security Architecture
**Trust Model**:
*   **Source of Truth**: The Backend validates sessions against the shared PostgreSQL database (BetterAuth schema) via `lib.auth.middleware`.
*   **Mechanism**:
    1.  Frontend sends `Authorization: Bearer <token>`.
    2.  Middleware checks `session` table for validity and expiry.
    3.  If valid, `user_id` is resolved and injected into the request scope.
*   **Internal Service Trust**: Trusted internal services can bypass token checks using the `X-User-ID` header (protected by network policies).

### 1.3 Persistence Strategy
**State Management**:
*   **LangGraph Checkpointing**: We use `AsyncPostgresSaver` (`lib.persistence.checkpointer`) to persist agent state.
    *   **Why**: Required for CopilotKit's async streaming protocol. `MemorySaver` is only a fallback.
    *   **Storage**: Serializes the entire graph state (messages, context, risk flags) into a binary blob stored in the `checkpoints` table.
*   **Recovery**: Thread IDs (passed from Frontend) allow users to resume conversations across page reloads.

### 1.4 Memory Architecture
**Triple-Store Design (`lib.memory.manager`)**:
1.  **User Profiles** (`flagpilot_user_profiles` Index):
    *   *Storage*: Elasticsearch.
    *   *Logic*: An LLM "Synthesizer" (`summarize_and_update`) runs asynchronously to merge new interactions into a concise profile summary.
2.  **Chat History** (`flagpilot_chat_history` Index):
    *   *Storage*: Raw message logs indexed by `user_id` and `session_id`.
3.  **Global Wisdom** (`flagpilot_global_wisdom` Index):
    *   *Storage*: Anonymized "lessons learned".
    *   *Logic*: When user feedback is positive (>0), the interaction is generalized and added here.
    *   *Retrieval*: Agents query this index (cosine similarity + keyword) to inject "community knowledge" into their prompts.

### 1.5 The Data Layer (Verified)

#### RAG Infrastructure (`lib/rag/pipeline.py`)
*   **Ingestion**:
    1.  Files are uploaded to MinIO (`minio_client.upload_file`).
    2.  Text is extracted (UTF-8/Latin-1 fallback).
    3.  **Chunking**: `RecursiveCharacterTextSplitter` (Size: 1000, Overlap: 200).
    4.  **Embedding**: `OpenAIEmbeddings` (`text-embedding-3-small`).
    5.  **Storage**: Qdrant (`flagpilot_documents` collection).
*   **Retrieval**: Standard cosine similarity search (k=5 default) with optional user_id filtering.

#### Persistence Layer
*   **Vector DB**: Qdrant running on port 6333.
    *   Collection: `flagpilot_documents`.
    *   Dimension: 1536 (OpenAI).
*   **Object Storage**: MinIO running on port 9000.
    *   Bucket: `flagpilot-files`.
    *   Path Structure: `{user_id}/{timestamp}_{uuid}.{ext}`.
*   **State Checkpoints**: PostgreSQL (`lib/persistence`). Used by LangGraph to persist conversation threads (`AsyncPostgresSaver`).
*   **Memory Store**: Elasticsearch (`es01:9200`).
    *   Stores: User Profiles, Chat History, Global Wisdom.

## 2. Component Analysis: The "Nitty Gritty"

### 2.1 The Agent Router Logic
Located in `agents/router.py`.
*   **Primary Logic**: LLM-based. It constructs a dynamic system prompt containing descriptions of all registered agents (`AGENT_REGISTRY`).
*   **Fallback Logic**: If the LLM router fails (exception), it falls back to `fallback_keyword_route()`, which checks for specific triggers (e.g., "contract" -> `contract-guardian`).
*   **Urgency Detection**: The Router also outputs an "urgency" level ("low", "medium", "high", "critical") which influences the `risk_level` state.

### 2.2 CopilotKit Integration
Located in `main.py` and `lib/copilotkit`.
*   The backend exposes a CopilotKit-compatible endpoint at `/copilotkit`.
*   It uses `add_langgraph_fastapi_endpoint` to tunnel the LangGraph `orchestrator_graph` directly to the frontend.
*   **Constraint**: This means the frontend interacts *directly* with the graph's state updates via SSE (Server-Sent Events).

## 3. Infrastructure Reality Map

| Service | Docker Host | Internal Dependencies Used |
| :--- | :--- | :--- |
| **Backend** | `backend` | Python 3.11, FastAPI |
| **PostgreSQL** | `postgres` | `asyncpg` (DB Access), `langgraph-checkpoint-postgres` |
| **Qdrant** | `qdrant` | `qdrant-client`, `langchain-qdrant` |
| **Elasticsearch** | `es01` | `elasticsearch` (Python Client) |
| **MinIO** | `minio` | `minio` (Python SDK) |
| **Redis** | `redis` | SPECIFICALLY used for Rate Limiting (`lib/rate_limit.py`) |

## 4. Validated Configuration Defaults
From `config.py` (Pydantic `BaseSettings`):
*   **LLM Model**: `kwaipilot/kat-coder-pro:free` (via OpenRouter).
*   **Embedding Model**: `text-embedding-3-small`.
*   **RAG Chunking**: 1000 chars / 200 overlap.
*   **Logging**: Loguru, rotating at 500 MB.
