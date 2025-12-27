# FlagPilot Backend v6.1 (Smart-Stack Edition)

## LangGraph Multi-Agent Architecture

AI-powered freelancer protection backend using **LangGraph** for multi-agent orchestration with **CopilotKit** for frontend integration.

### What's New in v6.1

- **AsyncPostgresSaver**: Async-compatible checkpointer for CopilotKit streaming
- **LLM Router**: Semantic agent selection replacing keyword matching
- **17 Agents**: Expanded from 14 specialized protection agents
- **PostgresStore**: Cross-thread long-term memory
- **Command Palette**: ⌘K quick actions on frontend

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FlagPilot Backend v6.1                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐    ┌─────────────────────────────────────────┐  │
│  │   FastAPI     │────│          CopilotKit Endpoint            │  │
│  │   /copilotkit │    │  (AG-UI Protocol, Streaming Events)     │  │
│  └───────────────┘    └─────────────────────────────────────────┘  │
│                                    │                                │
│                                    ▼                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                       LLM Router                                ││
│  │     Semantic task analysis → Agent selection with confidence    ││
│  │     File: agents/router.py                                      ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                    │                                │
│                                    ▼                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                  LangGraph Orchestrator                         ││
│  │  ┌──────────┐  ┌─────────────┐  ┌─────────────────────────────┐││
│  │  │  Plan    │──│   Execute   │──│      Synthesize           │ ││
│  │  │  Node    │  │   Agents    │  │  (LLM Summary)            │ ││
│  │  └──────────┘  └─────────────┘  └─────────────────────────────┘││
│  │       │              │                                          ││
│  │       │              ▼                                          ││
│  │       │    ┌───────────────────────────────────────────────┐   ││
│  │       │    │           17 Specialist Agents                │   ││
│  │       │    │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐│   ││
│  │       │    │  │ Contract    │ │ Job         │ │ Risk     ││   ││
│  │       │    │  │ Guardian    │ │ Authentictr │ │ Advisor  ││   ││
│  │       │    │  └─────────────┘ └─────────────┘ └──────────┘│   ││
│  │       │    │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐│   ││
│  │       │    │  │ Scope       │ │ Payment     │ │ Dispute  ││   ││
│  │       │    │  │ Sentinel    │ │ Enforcer    │ │ Mediator ││   ││
│  │       │    │  └─────────────┘ └─────────────┘ └──────────┘│   ││
│  │       │    │  + Communication, Negotiation, Profile,      │   ││
│  │       │    │    Ghosting, Talent, Application, Feedback,  │   ││
│  │       │    │    Planner + 3 NEW agents                    │   ││
│  │       │    └───────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Persistence Layer                            ││
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ ││
│  │  │ AsyncPostgres   │  │ PostgresStore   │  │ Elasticsearch   │ ││
│  │  │ Saver           │  │ (Long-term      │  │ (Memory,        │ ││
│  │  │ (Checkpoints)   │  │  Memory)        │  │  Wisdom)        │ ││
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐  │
│  │    RAGFlow Client       │  │       LangSmith Observability   │  │
│  │    (Knowledge Base)     │  │    (Tracing, Evaluation)        │  │
│  └─────────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| Agent Framework | LangGraph + LangChain |
| LLM | OpenRouter (configurable models) |
| Frontend Integration | CopilotKit AG-UI |
| State Persistence | AsyncPostgresSaver (PostgreSQL) |
| Long-term Memory | PostgresStore |
| Short-term Memory | Elasticsearch |
| RAG | RAGFlow |
| Observability | LangSmith |
| Cache | Redis |

### Directory Structure

```
backend/
├── agents/
│   ├── __init__.py
│   ├── agents.py           # Agent registry (17 agents)
│   ├── orchestrator.py     # Multi-agent supervisor
│   ├── router.py           # LLM-based agent selection (NEW)
│   └── roles/              # Individual agents (if applicable)
├── lib/
│   ├── copilotkit/
│   │   ├── graph.py        # LangGraph workflow
│   │   └── sdk.py          # CopilotKit endpoint
│   ├── persistence/        # (NEW)
│   │   ├── checkpointer.py # AsyncPostgresSaver factory
│   │   └── long_term_memory.py  # PostgresStore wrapper
│   ├── memory/
│   │   └── manager.py      # Elasticsearch memory
│   └── tools/
│       └── rag_tool.py     # RAG search utility
├── ragflow/
│   └── client.py           # RAGFlow SDK wrapper
├── routers/
│   ├── agents.py
│   ├── health.py
│   ├── rag.py
│   └── memory.py           # Memory API endpoints
├── tests/
│   ├── test_live_system.py # Integration tests
│   └── test_smart_stack.py # Smart-Stack feature tests (NEW)
├── config.py               # Settings + DATABASE_URL + LangSmith
├── main.py                 # FastAPI app
├── run.py                  # Entry point
├── Dockerfile
├── .env.example            # Environment template (NEW)
└── requirements-core.txt
```

### Environment Variables

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=kwaipilot/kat-coder-pro:free

# Database (PostgreSQL - for persistent state)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/flagpilot

# LangSmith (Optional but recommended)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=flagpilot

# RAGFlow
RAGFLOW_URL=http://ragflow:80
RAGFLOW_API_KEY=your-ragflow-key

# Elasticsearch
ES_HOST=es01
ES_PORT=9200

# Redis
REDIS_URL=redis://:password@redis:6379
```

### Quick Start

```bash
# With docker-compose (recommended)
docker-compose up -d

# Or build and run standalone
docker build -t flagpilot-backend .
docker run -p 8000:8000 --env-file .env flagpilot-backend
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service info |
| `GET /health` | Health check |
| `POST /copilotkit` | CopilotKit agent endpoint |
| `GET /api/agents` | List all agents (17) |
| `GET /api/agents/{id}` | Get agent details |
| `POST /api/v1/rag/ingest` | Ingest document |
| `GET /api/memory/wisdom` | Get global wisdom |
| `GET /api/memory/profile/{user_id}` | Get user profile |

### Agent Capabilities

| Agent | Specialization |
|-------|----------------|
| Contract Guardian | Legal risk analysis, clause review |
| Job Authenticator | Scam detection, job verification |
| Risk Advisor | Critical risk protocols (fast-fail) |
| Scope Sentinel | Scope creep detection |
| Payment Enforcer | Invoice collection strategies |
| Negotiation Assistant | Rate benchmarking, counter-offers |
| Communication Coach | Professional messaging |
| Dispute Mediator | Conflict resolution |
| Ghosting Shield | Client re-engagement |
| Profile Analyzer | Client vetting |
| Talent Vet | Candidate evaluation |
| Application Filter | Spam/AI detection |
| Feedback Loop | Outcome learning |
| Planner Role | Task breakdown |
| *+ 3 additional agents* | |

### Version History

- **v6.1.0** - Smart-Stack Edition (current)
  - AsyncPostgresSaver for async streaming
  - LLM Router for semantic agent selection
  - PostgresStore for long-term memory
  - 17 agents (up from 14)
  - CopilotKit UI control actions
  - Command Palette integration

- **v6.0.0** - LangGraph architecture
  - Complete migration from MetaGPT to LangGraph
  - Added LangSmith observability
  - LangGraph memory checkpointers
  - Simplified single-venv Docker setup

- **v5.x** - MetaGPT architecture (deprecated)
