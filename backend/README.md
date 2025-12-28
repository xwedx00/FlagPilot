# FlagPilot Backend v7.0

## Enterprise-Grade Multi-Agent Architecture

AI-powered freelancer protection backend using **LangGraph** for multi-agent orchestration with **Qdrant** vector search and **MinIO** file storage.

---

## ✨ What's New in v7.0

| Feature | Description |
|---------|-------------|
| **Qdrant Vector DB** | Replaced RAGFlow with Qdrant for document embeddings |
| **MinIO File Storage** | S3-compatible storage for contracts and documents |
| **AsyncPostgresSaver** | Async-compatible checkpointer for CopilotKit streaming |
| **LLM Router** | Semantic agent selection replacing keyword matching |
| **14 Specialist Agents** | Streamlined agent roster |
| **Fast-Fail Detection** | Programmatic scam signal detection before LLM calls |

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        FLAGPILOT BACKEND v7.0                                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                          API LAYER (FastAPI)                               │  │
│  │  /copilotkit  │  /api/agents  │  /api/v1/rag  │  /health  │  /health/rag  │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                            LLM ROUTER                                      │  │
│  │  Semantic Analysis → Confidence Scoring → Urgency Detection (low-critical) │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                      LANGGRAPH ORCHESTRATOR                                │  │
│  │                                                                            │  │
│  │     PLAN NODE  →  EXECUTE AGENTS (Parallel)  →  SYNTHESIZE NODE           │  │
│  │                                                                            │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │  │
│  │  │                    14 SPECIALIST AGENTS                              │   │  │
│  │  │  ⚖️ Contract Guardian  │  🔍 Job Authenticator  │  🚨 Risk Advisor   │   │  │
│  │  │  🎯 Scope Sentinel     │  💰 Payment Enforcer   │  🤝 Negotiation    │   │  │
│  │  │  💬 Communication      │  ⚔️ Dispute Mediator   │  👻 Ghosting Shield│   │  │
│  │  │  📊 Profile Analyzer   │  + 4 more specialized agents               │   │  │
│  │  └─────────────────────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                       PERSISTENCE LAYER                                    │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐ ┌────────┐ │  │
│  │  │  PostgreSQL  │ │Elasticsearch │ │    Qdrant    │ │  MinIO │ │ Redis  │ │  │
│  │  │  Checkpoints │ │   Wisdom     │ │  Embeddings  │ │  Files │ │ Cache  │ │  │
│  │  │  LangGraph   │ │  Profiles    │ │  RAG Search  │ │  S3 API│ │        │ │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────┘ └────────┘ │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
backend/
├── agents/                 # LangGraph agents
│   ├── router.py           # LLM-based agent routing
│   ├── orchestrator.py     # LangGraph workflow
│   └── definitions/        # 14 agent definitions
├── lib/
│   ├── vectorstore/        # Qdrant integration
│   │   └── qdrant_store.py
│   ├── storage/            # MinIO integration  
│   │   └── minio_client.py
│   ├── rag/                # RAG pipeline
│   │   └── pipeline.py
│   ├── memory/             # Elasticsearch memory
│   │   └── manager.py
│   └── persistence.py      # PostgreSQL checkpointer
├── routers/                # FastAPI routes
│   ├── rag.py              # RAG endpoints
│   ├── health.py           # Health checks
│   └── agents.py           # Agent endpoints
├── config.py               # Settings management
├── main.py                 # FastAPI application
└── requirements.txt        # Python dependencies
```

---

## 🔌 API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and version |
| `/health` | GET | Health status |
| `/health/services` | GET | Individual service health |
| `/copilotkit` | POST | CopilotKit AG-UI streaming |

### RAG (Qdrant + MinIO)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rag/ingest/text` | POST | Ingest text into Qdrant |
| `/api/v1/rag/ingest/file` | POST | Upload file to MinIO + embed in Qdrant |
| `/api/v1/rag/search` | POST | Semantic search in Qdrant |
| `/api/v1/rag/collection/info` | GET | Qdrant collection stats |
| `/api/v1/rag/files` | GET | List files in MinIO |

### Agents
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agents` | GET | List all agents |
| `/api/agents/{id}` | GET | Get agent details |

---

## 🧪 Testing

```bash
# Run full test suite (22 tests)
docker exec Flagpilot-backend python -m pytest tests/test_live_system.py -v

# View test output
docker exec Flagpilot-backend cat test_live_output.txt
```

### Test Categories
| Category | Tests | Description |
|----------|-------|-------------|
| Environment & Health | 6 | Service connectivity |
| Agent System | 3 | Agent registry & routing |
| RAG (Qdrant + MinIO) | 2 | Document ingestion & search |
| Orchestrator Scenarios | 6 | Full workflow tests |
| Memory Operations | 4 | ES memory CRUD |
| Integration | 1 | CopilotKit API |

---

## ⚙️ Configuration

### Required Environment Variables
```env
# LLM
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=kwaipilot/kat-coder-pro:free

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/flagpilot

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=flagpilot_documents

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=flagpilot-files

# Elasticsearch
ES_HOST=es01
ES_PORT=9200

# Redis
REDIS_URL=redis://redis:6379
```

---

## 📄 License

MIT License
