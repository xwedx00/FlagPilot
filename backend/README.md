# FlagPilot Backend - Developer Handbook
> **Technical Manual & Developer Guide** (v7.0)

## 🛠️ Setup Strategy

### 1. Environment Configuration
The system relies heavily on environment variables defined in `config.py`.
*   **Copy `.env.example` to `.env`**:
    ```bash
    cp .env.example .env
    ```
*   **Critical Variables**:
    *   `OPENROUTER_API_KEY`: Mandatory for Agent & Router intelligence.
    *   `DATABASE_URL`: Must point to Postgres.
    *   `QDRANT_HOST`: Default is `qdrant` (Docker) or `localhost` (Local Dev).

### 2. Running the System
**Option A: Full Docker (Production/Staging)**
Spins up everything including the backend API.
```bash
docker-compose up --build -d
```
*   **API**: `http://localhost:8000`
*   **MinIO Console**: `http://localhost:9001`

**Option B: Hybrid Dev (Local Python + Docker Infra)**
Best for development. Runs infra in Docker, backend on host for fast iterations.
```bash
# 1. Start Infrastructure
docker-compose up -d redis postgres qdrant minio es01

# 2. Install Dependencies (Use a venv)
pip install -r requirements.txt

# 3. Run Backend (Hot Reload)
uvicorn main:app --reload
```

## 🗺️ Annotated Directory Map

```text
backend/
├── main.py                     # App Entry Point. Configures CORS, CopilotKit, and Middleware.
├── config.py                   # Pydantic Settings. DEFINES ALL DEFAULTS (e.g., chunk size, db urls).
├── requirements.txt            # Prod dependencies. key: langgraph, qdrant-client, minio.
├── agents/
│   ├── agents.py               # DEFINES the 14 Agents (FlagPilotAgent class).
│   ├── orchestrator.py         # LOGIC CORE. LangGraph StateGraph, Routing, & Synthesis nodes.
│   └── router.py               # INTELLIGENCE. LLM-based routing logic + Scam Keyword checks.
├── lib/
│   ├── auth/                   # Middleware for JWT parsing (Frontend-driven).
│   ├── rag/
│   │   └── pipeline.py         # RAG Logic: MinIO Upload -> Text Split -> Qdrant Upsert.
│   ├── vectorstore/
│   │   └── qdrant_store.py     # Singleton Wrapper for QdrantClient + LangChain Store.
│   ├── storage/
│   │   └── minio_client.py     # Singleton Wrapper for MinIO file ops.
│   ├── persistence/            # AsyncPostgresSaver implementation for LangGraph checkpoints.
│   └── tools/                  # Auto-loaded tools for agents (Financial, Market, Legal).
└── routers/
    ├── agents.py               # Metadata endpoints (List agents).
    ├── rag.py                  # RAG Endpoints (Ingest, Search).
    └── health.py               # Deep health checks for all services.

## 🔧 Critical Module Configuration

### CopilotKit & LangGraph
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | Logic intelligence (LLM) | ✅ Yes |
| `DATABASE_URL` | Postgres connection for `AsyncPostgresSaver` checkpoints | ✅ Yes |

### Memory & Search
| Variable | Description | Required |
|----------|-------------|----------|
| `ES_HOST` | Elasticsearch Host (default: `es01`) | No (Fallback exists) |
| `QDRANT_HOST` | Vector DB Host (default: `qdrant`) | ✅ Yes |

### Storage
| Variable | Description | Required |
|----------|-------------|----------|
| `MINIO_ENDPOINT` | Object Storage (default: `minio:9000`) | ✅ Yes |
| `MINIO_Access_KEY` | MinIO User | ✅ Yes |

```

## 🔧 Troubleshooting & Logic Notes

### Common Issues
1.  **"Qdrant initialization failed"**:
    *   **Cause**: The `flagpilot_documents` collection logic in `qdrant_store.py` tries to create the collection on startup. If Qdrant is not healthy, the app crashes.
    *   **Fix**: Ensure `docker-compose up qdrant` is healthy before starting the backend.
2.  **"MinIO Connection Refused"**:
    *   **Cause**: `minio_client.py` connects to `minio:9000` by default. If running locally, set `MINIO_ENDPOINT=localhost:9000`.
3.  **"LLM Routing Failed"**:
    *   **Fallback**: If OpenRouter fails, `agents/router.py` catches the exception and falls back to `fallback_keyword_route`. Check logs for "LLM routing failed".

### Logic Quirks
*   **Scam Detection**: Is **Hybrid**.
    *   First, `detect_scam_signals` (regex/keywords) runs. If it hits, it **Bypasses** the LLM router and forces `risk-advisor`.
*   **Context Injection**:
    *   RAG Context (`k=3`) is *only* injected if `user_id` is present in the request.
*   **Agent Concurrent Execution**:
    *   Agents run in parallel via `asyncio.gather`. One slow agent will not block others, but synthesis waits for all.
