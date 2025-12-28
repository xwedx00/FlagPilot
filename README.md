<p align="center">
  <img src="https://img.shields.io/badge/FlagPilot-AI%20Agent%20Platform-6366F1?style=for-the-badge&logo=robot&logoColor=white" alt="FlagPilot">
</p>

<h1 align="center">🚀 FlagPilot v7.0</h1>

<p align="center">
  <strong>Enterprise-Grade AI Protection for Freelancers</strong>
  <br>
  <em>14 specialized LangGraph AI agents orchestrated to protect your freelance career</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-7.0.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B6B?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/CopilotKit-AG--UI-4ECDC4?style=flat-square&logo=react&logoColor=white" alt="CopilotKit">
  <img src="https://img.shields.io/badge/Qdrant-Vector%20DB-dc382d?style=flat-square" alt="Qdrant">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
</p>

---

## 🎯 What is FlagPilot?

**FlagPilot** is an enterprise-grade AI platform designed specifically for freelancers. Built on **LangGraph** and **LangChain** with **Qdrant** vector search and **MinIO** file storage, it orchestrates 14 specialized AI agents that work together to:

| Capability | Description |
|------------|-------------|
| 📜 **Contract Analysis** | Detect legal risks, unfavorable clauses, missing protections |
| 🔍 **Scam Detection** | Fast-fail protection with 5+ scam signal patterns |
| 🎯 **Scope Creep Prevention** | Identify boundary violations before they escalate |
| 💰 **Payment Enforcement** | Collection strategies and late fee policies |
| 🤝 **Negotiation Assistance** | Rate benchmarking and counter-offer strategies |
| 🧠 **Learning Memory** | Elasticsearch wisdom + Qdrant vector search |

---

## 🏗️ System Architecture v7.0

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           FLAGPILOT v7.0 ARCHITECTURE                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              FRONTEND LAYER                                 │ │
│  │    Next.js 15  │  CopilotKit AG-UI  │  Shadcn + GSAP  │  Better Auth       │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              BACKEND LAYER                                  │ │
│  │  FastAPI  │  LangGraph Orchestrator  │  LLM Router  │  14 Specialist Agents│ │
│  │                                                                             │ │
│  │  Endpoints:  /copilotkit  │  /api/agents  │  /api/v1/rag  │  /health       │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           PERSISTENCE LAYER                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  ┌───────┐ │ │
│  │  │ PostgreSQL  │  │Elasticsearch│  │   Qdrant    │  │  MinIO  │  │ Redis │ │ │
│  │  │ Checkpoints │  │   Wisdom    │  │  Embeddings │  │  Files  │  │ Cache │ │ │
│  │  │ LangGraph   │  │  Profiles   │  │  RAG Search │  │  S3 API │  │       │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  └───────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           EXTERNAL SERVICES                                 │ │
│  │       OpenRouter (LLM)      │      LangSmith (Observability)                │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Agent Roster (14 Agents)

### Protection Agents
| Agent | Role | Specialization |
|-------|------|----------------|
| ⚖️ **Contract Guardian** | Legal Analyst | Risk clauses, IP terms, payment terms |
| 🔍 **Job Authenticator** | Scam Detective | Scam patterns, red flags, verification |
| 🚨 **Risk Advisor** | Emergency Override | Critical warnings, immediate actions |
| 🎯 **Scope Sentinel** | Scope Protector | Scope creep, change orders, boundaries |

### Business Agents
| Agent | Role | Specialization |
|-------|------|----------------|
| 💰 **Payment Enforcer** | Collection Specialist | Late fees, invoices, collection strategies |
| 🤝 **Negotiation Assistant** | Deal Maker | Rate benchmarking, counter-offers |
| 💬 **Communication Coach** | Messaging Expert | Professional responses |
| ⚔️ **Dispute Mediator** | Conflict Resolver | Escalation paths, resolution strategies |

### Intelligence Agents
| Agent | Role | Specialization |
|-------|------|----------------|
| 👻 **Ghosting Shield** | Client Tracker | Re-engagement, follow-up sequences |
| 📊 **Profile Analyzer** | Client Vetter | Background research, risk scoring |

---

## 🚀 Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/flagpilot.git
cd flagpilot
cp backend/.env.example backend/.env
```

### 2. Set Environment Variables

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=kwaipilot/kat-coder-pro:free

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/flagpilot

# Qdrant (Vector DB)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=flagpilot_documents

# MinIO (File Storage)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=flagpilot-files

# Optional
LANGSMITH_API_KEY=lsv2_pt_your-key
```

### 3. Start with Docker

```bash
docker-compose up -d --build
```

### 4. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| MinIO Console | http://localhost:9001 |

---

## ⚙️ Configuration Reference

### Required Variables
| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access |
| `OPENROUTER_MODEL` | Model ID (e.g., `kwaipilot/kat-coder-pro:free`) |

### Database & Persistence
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `ES_HOST` | Elasticsearch host | `es01` |
| `ES_PORT` | Elasticsearch port | `9200` |

### Qdrant (Vector Database)
| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant server host | `qdrant` |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `QDRANT_COLLECTION` | Collection name | `flagpilot_documents` |

### MinIO (File Storage)
| Variable | Description | Default |
|----------|-------------|---------|
| `MINIO_ENDPOINT` | MinIO server endpoint | `minio:9000` |
| `MINIO_ACCESS_KEY` | Access key | `minioadmin` |
| `MINIO_SECRET_KEY` | Secret key | `minioadmin` |
| `MINIO_BUCKET` | Default bucket | `flagpilot-files` |

---

## 🧪 Testing

```bash
# Run full test suite
docker exec Flagpilot-backend python -m pytest tests/test_live_system.py -v

# View detailed output
docker exec Flagpilot-backend cat test_live_output.txt
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Agent Framework | LangGraph + LangChain |
| LLM Provider | OpenRouter |
| State Persistence | AsyncPostgresSaver |
| Vector Database | Qdrant |
| File Storage | MinIO (S3-compatible) |
| Search/Memory | Elasticsearch 9.2 |
| Cache | Redis |
| Observability | LangSmith |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| UI Library | Shadcn UI |
| AI Integration | CopilotKit AG-UI |
| Authentication | Better Auth |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Container | Docker Compose |
| Database | PostgreSQL |
| Vector DB | Qdrant 1.16+ |
| Search | Elasticsearch 9.2 |
| Storage | MinIO |
| Cache | Redis |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with ❤️ for freelancers worldwide</strong>
</p>
