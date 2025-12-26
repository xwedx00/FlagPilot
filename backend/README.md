# FlagPilot Backend v6.0

## LangGraph Multi-Agent Architecture

AI-powered freelancer protection backend using **LangGraph** for multi-agent orchestration with **CopilotKit** for frontend integration.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                       FlagPilot Backend v6.0                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐    ┌─────────────────────────────────────────┐  │
│  │   FastAPI     │────│          CopilotKit Endpoint            │  │
│  │   /copilotkit │    │  (AG-UI Protocol, Streaming Events)     │  │
│  └───────────────┘    └─────────────────────────────────────────┘  │
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
│  │       │    │           14 Specialist Agents                │   ││
│  │       │    │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐│   ││
│  │       │    │  │ Contract    │ │ Job         │ │ Risk     ││   ││
│  │       │    │  │ Guardian    │ │ Authentictr │ │ Advisor  ││   ││
│  │       │    │  └─────────────┘ └─────────────┘ └──────────┘│   ││
│  │       │    │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐│   ││
│  │       │    │  │ Scope       │ │ Payment     │ │ Dispute  ││   ││
│  │       │    │  │ Sentinel    │ │ Enforcer    │ │ Mediator ││   ││
│  │       │    │  └─────────────┘ └─────────────┘ └──────────┘│   ││
│  │       │    │  + Communication, Negotiation, Profile,      │   ││
│  │       │    │    Ghosting, Talent, Application, Feedback   │   ││
│  │       │    └───────────────────────────────────────────────┘   ││
│  │       │                                                         ││
│  │       └─────▶ Deep Agent (Complex Tasks)                       ││
│  │                - Planning (TodoList)                            ││
│  │                - Subagent Delegation                            ││
│  │                - Filesystem Memory                              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐  │
│  │    RAGFlow Client       │  │   Elasticsearch Memory          │  │
│  │    (Knowledge Base)     │  │   (User Profiles, Wisdom)       │  │
│  └─────────────────────────┘  └─────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      LangSmith Observability                    ││
│  │                 (Tracing, Evaluation, Debugging)                ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### Key Features

- **🔗 LangGraph Orchestration**: Multi-agent supervisor pattern with parallel execution
- **🚨 Fast-Fail Risk Detection**: Programmatic scam detection before LLM calls
- **🧠 Deep Agents**: Complex multi-step tasks with planning and subagent delegation
- **📚 RAG Integration**: RAGFlow for personal vault and global wisdom
- **💾 Memory Persistence**: LangGraph checkpointers + Elasticsearch
- **📊 LangSmith Observability**: Full tracing and evaluation
- **🤖 CopilotKit Integration**: AG-UI protocol streaming

### Technology Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| Agent Framework | LangGraph |
| LLM | OpenRouter (configurable models) |
| Frontend Integration | CopilotKit |
| RAG | RAGFlow |
| Memory | Elasticsearch + LangGraph MemorySaver |
| Observability | LangSmith |
| Complex Tasks | Deep Agents |

### Directory Structure

```
backend/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # LangGraph base classes
│   ├── orchestrator.py     # Multi-agent supervisor
│   ├── deep_agent.py       # Complex task handler
│   ├── registry.py         # Agent registry
│   └── roles/              # Individual agents
│       ├── contract_guardian.py
│       ├── job_authenticator.py
│       ├── risk_advisor.py
│       ├── scope_sentinel.py
│       ├── payment_enforcer.py
│       ├── negotiation_assistant.py
│       ├── communication_coach.py
│       ├── dispute_mediator.py
│       ├── ghosting_shield.py
│       ├── profile_analyzer.py
│       ├── talent_vet.py
│       ├── application_filter.py
│       ├── feedback_loop.py
│       └── planner_role.py
├── lib/
│   ├── copilotkit/
│   │   ├── graph.py        # LangGraph workflow
│   │   └── sdk.py          # CopilotKit endpoint
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
│   └── feedback.py
├── config.py               # Settings + LangSmith
├── main.py                 # FastAPI app
├── run.py                  # Entry point
├── Dockerfile
└── requirements-core.txt
```

### Environment Variables

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

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
REDIS_URL=redis://redis:6379
```

### Quick Start

```bash
# Build and run with Docker
docker build -t flagpilot-backend .
docker run -p 8000:8000 --env-file .env flagpilot-backend

# Or with docker-compose
docker-compose up backend
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service info |
| `GET /health` | Health check |
| `POST /copilotkit` | CopilotKit agent endpoint |
| `GET /api/agents` | List all agents |
| `GET /api/agents/{id}` | Get agent details |
| `POST /api/v1/rag/ingest` | Ingest document |

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

### Version History

- **v6.0.0** - LangGraph architecture (current)
  - Complete migration from MetaGPT to LangGraph
  - Added LangSmith observability
  - Added Deep Agents for complex tasks
  - LangGraph memory checkpointers
  - Simplified single-venv Docker setup

- **v5.x** - MetaGPT architecture (deprecated)
  - Multi-venv isolation pattern
  - Subprocess-based agent execution
