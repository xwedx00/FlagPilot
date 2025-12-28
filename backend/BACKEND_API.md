# Backend API Reference (v7.0)
**Logic-First Documentation**

## 🧠 CopilotKit Protocol
### `POST /copilotkit`
**Security Headers**:
*   `Authorization`: `Bearer <session_token>` (Validated against DB)
*   `X-Copilot-Session-ID`: (Optional) For threading context.

**Stream Format (SSE)**:
The endpoint streams Server-Sent Events (SSE) representing graph updates:
1.  `event: encoding` -> JSON defining State schema.
2.  `event: chunk` -> Partial JSON patches for `messages` (token streaming).
3.  `event: state` -> Full state snapshots (e.g., status updates).

**Logic Flow**:
1.  **Handshake**: Establishes a connection with the frontend CopilotKit SDK.
2.  **Graph Tunnel**: Instantiates the `orchestrator_graph` (`agents/orchestrator.py`).
3.  **Execution**: Streaming response of LangGraph events (node starts, token stream, node ends).
4.  **Persistence**: Uses the session ID to save/load checkpoints from PostgreSQL.

## 📚 RAG & Data Endpoints (`routers/rag.py`)

### `POST /api/v1/rag/ingest/text`
**Internal Logic**:
1.  **Auth**: Validates user via `require_auth` middleware.
2.  **Chunking**: Splits text (size=1000, overlap=200).
3.  **Embedding**: Calls OpenRouter/OpenAI for embeddings.
4.  **Vector Store**: Upserts to Qdrant collection `flagpilot_documents`.
5.  **Return**: Returns the number of chunks created.

**Payload**:
```json
{
  "text": "The freelancer contract states...",
  "source": "contract_v1.txt",
  "metadata": {"type": "contract"}
}
```

### `POST /api/v1/rag/ingest/file`
**Internal Logic**:
1.  **MinIO Upload**: Streams file directly to MinIO bucket `flagpilot-files`.
2.  **Read-Back**: Reads the file stream again for text extraction.
3.  **Processing**: Decodes (UTF-8/Latin-1) -> Chunks -> Embeds -> Qdrant.
4.  **Metadata**: Tags Qdrant vectors with the MinIO object path for linkage.

**Payload**: `multipart/form-data` with file field.

### `POST /api/v1/rag/search`
**Internal Logic**:
1.  **Embed Query**: Converts query string to vector.
2.  **Similarity Search**: Queries Qdrant for nearest neighbors (`k=5`).
3.  **Score Filtering**: (Optional internal logic) Filters low-confidence results.
4.  **Format**: Returns list of `SearchResult` objects including raw content and metadata.

**Payload**:
```json
{
  "query": "What are the payment terms?",
  "k": 5
}
```

## 🤖 Agent Metadata (`routers/agents.py`)

### `GET /api/agents`
**Logic**: Returns a static list of all 14 agents defined in `agents/agents.py`, including their specialized system prompts and credit costs.

## 🩺 System Health (`routers/health.py`)

### `GET /health/services`
**Logic**: Performs active connectivity tests (not just a static 200 OK):
1.  **Redis**: PINGS the instance.
2.  **Qdrant**: Fetches collection list.
3.  **Elasticsearch**: Checks cluster info.
4.  **MinIO**: Lists buckets.
5.  **Postgres**: Executes `SELECT version()`.
**Return**: JSON object with individual status for each service.
