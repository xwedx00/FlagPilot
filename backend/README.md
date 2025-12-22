# FlagPilot Backend 🚀

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-00CED1?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/MetaGPT-Multi--Agent-FF6B6B?style=flat-square&logo=openai&logoColor=white" alt="MetaGPT">
  <img src="https://img.shields.io/badge/RAGFlow-Knowledge%20Engine-4ECDC4?style=flat-square&logo=elasticsearch&logoColor=white" alt="RAGFlow">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
</p>

The intelligent core of **FlagPilot**—an AI-driven multi-agent system that protects freelancers from bad clients, scams, and scope creep.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [AI Agents](#-ai-agents)
- [Core Features](#-core-features)
- [Setup & Installation](#-setup--installation)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Directory Structure](#-directory-structure)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

The FlagPilot backend is a **pure MetaGPT agent server** built with FastAPI. It orchestrates 17 specialized AI agents that collaborate to analyze contracts, verify job leads, detect scams, and provide strategic advice to freelancers.

### Key Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async web framework with native SSE support |
| **MetaGPT** | Multi-agent orchestration framework |
| **RAGFlow** | Retrieval-Augmented Generation for knowledge base |
| **OpenRouter** | LLM gateway for accessing various models |
| **Elasticsearch** | Memory system (profiles, chat history, wisdom) |
| **CopilotKit** | Frontend integration SDK |
| **Redis** | Session caching and real-time pub/sub |

### Multi-Venv Architecture

The backend uses **4 isolated virtual environments** to prevent dependency conflicts:

```
┌─────────────────────────────────────────────────────────────┐
│   Core (/usr/local)     │  FastAPI, uvicorn, pydantic      │
├─────────────────────────────────────────────────────────────┤
│   venv-copilotkit       │  copilotkit, langgraph, openai   │
├─────────────────────────────────────────────────────────────┤
│   venv-metagpt          │  metagpt==0.8.1                  │
├─────────────────────────────────────────────────────────────┤
│   venv-ragflow          │  ragflow-sdk, elasticsearch      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                      FastAPI Application Layer                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   /api/agents    │  │   /api/team      │  │   /api/rag       │  │
│  │  Agent Registry  │  │  Team Workflow   │  │  RAG Search      │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │            │
│  ┌────────▼─────────────────────▼─────────────────────▼────────┐   │
│  │                   FlagPilot Orchestrator                    │   │
│  │            (Multi-Agent Coordination)                       │   │
│  └──────────────────────────────┬──────────────────────────────┘   │
│                                 │                                  │
│  ┌──────────────────────────────▼──────────────────────────────┐   │
│  │                    Agent Pool (17 Agents)                   │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │   │
│  │  │ Contract   │ │   Job      │ │   Scope    │ │  Risk    │  │   │
│  │  │ Guardian   │ │Authenticator│ │ Sentinel   │ │ Advisor │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │   │
│  │  │ Payment    │ │Negotiation │ │   Dispute  │ │ Ghosting │  │   │
│  │  │ Enforcer   │ │ Assistant  │ │  Mediator  │ │  Shield  │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │   │
│  │  │ Communicate│ │ Application│ │  Feedback  │ │ Profile  │  │   │
│  │  │   Coach    │ │  Filter    │ │    Loop    │ │ Analyzer │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │   │
│  │         ... and more specialized agents                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    RAGFlow Integration                      │   │
│  │    Global Wisdom DB · Tiered Context · Document Retrieval   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **Client Request** → FastAPI receives the workflow request via REST/SSE
2. **Orchestrator Planning** → FlagPilot Orchestrator plans agent tasks
3. **Agent Execution** → Agents execute their assigned tasks in parallel/sequence
4. **RAG Enhancement** → Agents query Global Wisdom for relevant strategies
5. **Fast-Fail Check** → If CRITICAL_RISK detected, workflow aborts immediately
6. **Response Streaming** → Results streamed back to client via SSE

---

## 🤖 AI Agents

### Agent Registry

All agents are **automatically discovered** from `agents/roles/` on startup.

| Module | Agent Class | Responsibility |
|--------|-------------|----------------|
| `Flagpilot_orchestrator.py` | `FlagPilotOrchestrator` | Team lead, task planning & coordination |
| `contract_guardian.py` | `ContractGuardian` | Legal analysis & contract review |
| `job_authenticator.py` | `JobAuthenticator` | Scam detection with Fast-Fail |
| `scope_sentinel.py` | `ScopeSentinel` | Scope creep identification |
| `risk_advisor.py` | `RiskAdvisor` | Emergency guidance override |
| `payment_enforcer.py` | `PaymentEnforcer` | Payment term protection |
| `negotiation_assistant.py` | `NegotiationAssistant` | Deal-making strategies |
| `communication_coach.py` | `CommunicationCoach` | Professional messaging |
| `dispute_mediator.py` | `DisputeMediator` | Conflict resolution |
| `ghosting_shield.py` | `GhostingShield` | Client tracking & follow-up |
| `application_filter.py` | `ApplicationFilter` | Job matching & filtering |
| `feedback_loop.py` | `FeedbackLoop` | Learning from outcomes |
| `planner_role.py` | `PlannerRole` | Complex task breakdown |
| `profile_analyzer.py` | `ProfileAnalyzer` | Client reputation analysis |
| `talent_vet.py` | `TalentVet` | Collaborator vetting |

### Agent Communication Schema

All agents output a standardized risk schema:

```json
{
  "analysis": "Detailed analysis text...",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "is_critical_risk": false,
  "recommendations": ["Action 1", "Action 2"],
  "confidence": 0.85
}
```

---

## 🛡 Core Features

### 1. Fast-Fail Mechanism 🚨

When any agent detects a **CRITICAL_RISK**, the system:

1. **Immediately aborts** all pending tasks
2. **Injects** the `RiskAdvisor` agent dynamically
3. **Streams** emergency protocols to the client
4. **Logs** the incident for analysis

```python
# Trigger conditions (in any agent's response):
{
    "is_critical_risk": True,
    "risk_level": "CRITICAL"
}
```

### 2. Global Wisdom RAG 🧠

Agents query a shared knowledge base of successful freelance strategies:

- **5-star rated** strategies from experienced freelancers
- **Tiered context injection** based on agent role
- **Semantic search** via ElasticSearch
- **Document types**: Contracts, negotiations, client communications

### 3. SSE Streaming 📡

Real-time workflow updates via Server-Sent Events:

```javascript
// Event types
event: message        // Agent text output
event: agent_status   // Agent working/completed/error
event: workflow_update // Workflow progress data
```

### 4. Workflow Persistence 💾

All executions are saved for:
- Historical analysis
- Pattern detection
- Continuous improvement
- User review

---

## Authentication & Security
- **Auth**: Expects `Authorization: Bearer <user_id>` header.
- **Isolation**: Agent state is scoped to `user_id` to prevent data leakage.
- **Protocol**: Implements CopilotKit Python SDK for frontend integration.

## Usage
Run with Docker or locally:
```bash
python main.py
```
API Documentation available at `/docs` (Swagger UI).

---

## 🚀 Setup & Installation

### Prerequisites

- Docker & Docker Compose v2.0+
- OpenRouter API key
- 4GB+ RAM (8GB recommended)

### Quick Start (Docker)

```bash
# From project root
docker compose up --build

# Backend available at http://localhost:8000
```

### Local Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
python run.py
```

---

## ⚙ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# ===========================================
# LLM Configuration (OpenRouter)
# ===========================================
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# ===========================================
# Redis (Cache only - no database needed)
# ===========================================
REDIS_URL=redis://:password@redis:6379

# ===========================================
# RAGFlow
# ===========================================
RAGFLOW_URL=http://ragflow:80
RAGFLOW_API_KEY=your-ragflow-key

# ===========================================
# Application
# ===========================================
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-prod
```

### Configuration Priority

1. Environment variables (highest)
2. `.env` file
3. Default values in `config.py`

---

## 📚 API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info & available endpoints |
| `GET` | `/health` | Health check with agent list |

### Agent Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/agents` | List all registered agents |
| `GET` | `/api/agents/{name}` | Get agent details |
| `POST` | `/api/agents/{name}/execute` | Execute single agent |

### Team Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/team/chat` | Start multi-agent workflow (SSE) |

### RAG Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/rag/search` | Search knowledge base |
| `POST` | `/api/rag/upload` | Upload documents |

> 📖 **See [BACKEND_API.md](./BACKEND_API.md) for complete API documentation**

---

## 📁 Directory Structure

```
backend/
├── agents/                     # MetaGPT agent system
│   ├── roles/                  # Agent implementations (17 agents)
│   ├── prompts/                # Agent prompt templates
│   ├── registry.py             # Auto-discovery & registration
│   └── team.py                 # Team orchestration logic
│
├── lib/                        # Shared utilities
│   ├── memory/                 # Elasticsearch Memory System
│   │   └── manager.py          # MemoryManager (profiles, chat, wisdom)
│   ├── copilotkit/             # CopilotKit SDK integration
│   │   ├── graph.py            # LangGraph workflow
│   │   └── sdk.py              # SDK setup
│   ├── runners/                # Subprocess runners for isolated venvs
│   │   ├── copilotkit_runner.py
│   │   ├── metagpt_runner.py
│   │   └── ragflow_runner.py
│   └── auth/                   # Authentication middleware
│
├── routers/                    # FastAPI route handlers
│   ├── agents.py               # /api/agents endpoints
│   ├── health.py               # /health endpoints
│   └── rag.py                  # /api/rag endpoints
│
├── tests/                      # Test suites
│   ├── test_live_system.py     # Live integration tests (12 tests)
│   └── integration/            # Integration tests
│
├── requirements-core.txt       # Core dependencies
├── requirements-copilotkit.txt # CopilotKit venv deps
├── requirements-metagpt.txt    # MetaGPT venv deps
├── requirements-ragflow.txt    # RAGFlow venv deps
├── config.py                   # Pydantic configuration
├── main.py                     # FastAPI app entry point
├── Dockerfile                  # Multi-venv container build
├── BACKEND_API.md              # API documentation
├── TEST_REPORT.md              # Test verification report
└── README.md                   # This file
```

---

## 🧪 Testing

### Running Tests

```bash
# Inside Docker (Recommended)
docker exec Flagpilot-backend pytest tests/test_live_system.py -v

# Verbose with all LLM calls and responses
docker exec Flagpilot-backend pytest tests/test_live_system.py -v -s --log-cli-level=DEBUG

# All tests (integration + live)
docker exec Flagpilot-backend pytest tests/ -v

# With coverage
docker exec Flagpilot-backend pytest tests/ --cov=. --cov-report=html
```

### Test Categories

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_live_system.py` | 12 | Full integration: LLM + RAG + ES Memory + MetaGPT |
| `integration/test_copilotkit_integration.py` | 14 | API endpoints + subprocess runners |
| `integration/test_api.py` | 6 | Core API functionality |

---

## 🔧 Troubleshooting

### Common Issues

#### MetaGPT Token Warnings

Benign warnings like "usage calculation failed" are automatically suppressed. These occur when using custom models via OpenRouter.

#### Agent Not Found

```
Error: Agent 'my-agent' not found in registry
```

**Solution**: Ensure your agent class is in `agents/roles/` and extends `Role` from MetaGPT.

#### RAGFlow Connection Failed

```
Error: Cannot connect to RAGFlow at http://ragflow:80
```

**Solution**: Wait for RAGFlow to fully initialize (can take 2-3 minutes on first start).

#### Docker Memory Issues

```
Error: Container killed due to memory limits
```

**Solution**: Increase Docker memory to 8GB+ (ElasticSearch is hungry).

### Logs

```bash
# View backend logs
docker logs Flagpilot-backend -f

# Application logs (inside container)
docker exec Flagpilot-backend cat logs/Flagpilot.log
```

---

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

<p align="center">
  <strong>Built with ❤️ using MetaGPT & FastAPI</strong>
</p>
