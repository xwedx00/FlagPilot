# FlagPilot Backend API Reference v7.0

## Overview

FlagPilot Backend v7.0 is a **LangGraph-based multi-agent system** for freelancer protection, integrated with CopilotKit, Qdrant vector search, and MinIO file storage.

**Base URL**: `http://localhost:8000`

---

## Endpoints

### Health & Status

#### `GET /`
Service information and available endpoints.

**Response**:
```json
{
  "name": "FlagPilot Agent API",
  "version": "7.0.0",
  "agents": 14,
  "architecture": "LangGraph + CopilotKit + Qdrant + PostgreSQL",
  "endpoints": {
    "copilotkit": "/copilotkit",
    "agents": "/api/agents",
    "rag": "/api/v1/rag",
    "health": "/health"
  }
}
```

#### `GET /health`
Health check with feature list.

**Response**:
```json
{
  "status": "healthy",
  "version": "7.0.0",
  "timestamp": "2024-12-28T12:00:00Z",
  "agents": ["contract-guardian", "job-authenticator", ...],
  "features": [
    "LangGraph Team Orchestration",
    "Qdrant Vector RAG",
    "MinIO File Storage",
    "CopilotKit Protocol Streaming",
    "LangSmith Observability",
    "Elasticsearch Memory",
    "PostgreSQL Checkpoints"
  ]
}
```

#### `GET /health/services`
Individual service health status.

**Response**:
```json
{
  "redis": {"status": "healthy", "message": "Connected"},
  "qdrant": {"status": "healthy", "message": "Connected, 1 collections"},
  "elasticsearch": {"status": "healthy", "message": "Connected, version 9.2.3"},
  "minio": {"status": "healthy", "message": "Connected, 1 buckets"},
  "postgresql": {"status": "healthy", "message": "Connected"}
}
```

#### `GET /health/rag`
RAG pipeline health (Qdrant + MinIO).

---

### CopilotKit Integration

#### `POST /copilotkit`
Primary endpoint for CopilotKit AG-UI protocol.

**Request**: CopilotKit AG-UI message format
**Response**: Server-Sent Events (SSE) stream

---

### RAG Endpoints (Qdrant + MinIO)

#### `POST /api/v1/rag/ingest/text`
Ingest text content into Qdrant vector database.

**Request**:
```json
{
  "text": "Contract terms and conditions...",
  "source": "contract_v1",
  "user_id": "user123"
}
```

**Response**:
```json
{
  "success": true,
  "chunk_count": 3,
  "source": "contract_v1"
}
```

#### `POST /api/v1/rag/ingest/file`
Upload file to MinIO and embed content in Qdrant.

**Request**: `multipart/form-data` with file
**Response**:
```json
{
  "success": true,
  "object_name": "user123/contract.pdf",
  "chunk_count": 5
}
```

#### `POST /api/v1/rag/search`
Semantic search in Qdrant.

**Request**:
```json
{
  "query": "payment terms for freelancers",
  "k": 5,
  "user_id": "user123"
}
```

**Response**:
```json
{
  "results": [
    {"content": "...", "score": 0.92, "source": "contract_v1"},
    {"content": "...", "score": 0.87, "source": "guide_v2"}
  ]
}
```

#### `GET /api/v1/rag/collection/info`
Get Qdrant collection statistics.

#### `GET /api/v1/rag/files`
List files in MinIO bucket.

#### `GET /api/v1/rag/files/{object_name}/url`
Get presigned URL for file download.

---

### Agent Endpoints

#### `GET /api/agents`
List all available agents.

**Response**:
```json
{
  "agents": [
    {"id": "contract-guardian", "name": "Contract Guardian", "description": "..."},
    {"id": "job-authenticator", "name": "Job Authenticator", "description": "..."}
  ],
  "count": 14
}
```

#### `GET /api/agents/{agent_id}`
Get specific agent details.

---

## Authentication

Currently no authentication required for local development.

---

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
