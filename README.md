<p align="center">
  <img src="https://img.shields.io/badge/FlagPilot-AI%20Agent%20Platform-6366F1?style=for-the-badge&logo=robot&logoColor=white" alt="FlagPilot">
</p>

<h1 align="center">🚀 FlagPilot</h1>

<p align="center">
  <strong>Your AI-Powered Freelancer Protection Platform</strong>
  <br>
  <em>15 specialized AI agents working together to protect you from bad clients, scams, and scope creep</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-00CED1?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/MetaGPT-Multi--Agent-FF6B6B?style=flat-square&logo=openai&logoColor=white" alt="MetaGPT">
  <img src="https://img.shields.io/badge/RAGFlow-Knowledge%20Engine-4ECDC4?style=flat-square&logo=elasticsearch&logoColor=white" alt="RAGFlow">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
</p>

---

## 📖 Table of Contents

- [🎯 What is FlagPilot?](#-what-is-Flagpilot)
- [✨ Key Features](#-key-features)
- [🤖 AI Agent Roster](#-ai-agent-roster)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Configuration](#️-configuration)
- [📚 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 What is FlagPilot?

**FlagPilot** is an intelligent AI platform designed specifically for freelancers. Built on top of [MetaGPT](https://github.com/geekan/MetaGPT) and [RAGFlow](https://github.com/infiniflow/ragflow), it orchestrates a team of 15 specialized AI agents that work together to:

- **Analyze contracts** for legal risks and unfavorable terms
- **Detect scams** and verify job leads before you commit
- **Identify scope creep** before it happens
- **Provide legal guidance** and negotiation strategies
- **Learn from a global database** of successful freelance strategies

> 💡 **Think of FlagPilot as your personal team of AI advisors**—a lawyer, a fraud investigator, a negotiator, and more—all working 24/7 to protect your freelance career.

---

## ✨ Key Features

### 🚨 Fast-Fail Risk Detection
When **ANY** agent detects a critical risk (scam pattern, unenforceable contract, known bad actor), the entire workflow **immediately halts**. A specialized `RiskAdvisor` is dynamically injected to provide emergency protocols and safety guidance.

```
User submits job lead → JobAuthenticator detects scam patterns
                                    ↓
            ⚠️ CRITICAL_RISK DETECTED → Workflow ABORTS
                                    ↓
            RiskAdvisor provides emergency safety protocols
```

### 🧠 Global Wisdom RAG
Agents don't just "guess"—they retrieve **5-star rated strategies** from a curated knowledge base of successful freelance practices and apply them to your specific situation.

### 📊 Real-Time SSE Streaming
Watch your AI team work in real-time with Server-Sent Events (SSE) streaming. See agent status updates, workflow progress, and results as they happen.

### 💾 Workflow Persistence
Every interaction is saved. Review past analyses, track patterns, and build your personal knowledge base over time.

### ⚡ Smart Orchestration
The system automatically optimizes workflows:
- **Direct Response**: Simple queries (e.g., greetings) bypass the full agent team for instant responses.
- **Dynamic Routing**: Complex tasks are routed only to relevant agents, saving tokens and time.

---

## 🤖 AI Agent Roster

FlagPilot deploys **15 specialized AI agents**, each with a unique role:

| Agent | Role | Description |
|-------|------|-------------|
| 🎯 **FlagPilot Orchestrator** | Team Lead | Plans and coordinates all agent activities using DAG-based task scheduling |
| ⚖️ **Contract Guardian** | Legal Analyst | Analyzes contracts for risks, unfavorable clauses, and legal vulnerabilities |
| 🔍 **Job Authenticator** | Scam Detective | Detects scam patterns, verifies job legitimacy with Fast-Fail capability |
| 🎯 **Scope Sentinel** | Scope Protector | Identifies scope creep indicators and boundary violations |
| 🚨 **Risk Advisor** | Emergency Override | Provides critical safety protocols when high-risk situations are detected |
| 💰 **Payment Enforcer** | Payment Protector | Ensures payment terms are fair and enforceable |
| 🤝 **Negotiation Assistant** | Deal Maker | Provides negotiation strategies and counteroffers |
| 💬 **Communication Coach** | Messaging Expert | Crafts professional responses and client communications |
| ⚔️ **Dispute Mediator** | Conflict Resolver | Guides through dispute resolution processes |
| 👻 **Ghosting Shield** | Client Tracker | Identifies ghosting patterns and provides follow-up strategies |
| 📝 **Application Filter** | Job Matcher | Filters job applications based on your criteria and red flags |
| 🔄 **Feedback Loop** | Learning Engine | Analyzes outcomes to improve future recommendations |
| 📋 **Planner Role** | Task Planner | Breaks down complex requests into actionable steps |
| 👤 **Profile Analyzer** | Client Profiler | Analyzes client history and reputation |
| 🎭 **Talent Vet** | Talent Evaluator | Vets potential collaborators and subcontractors |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FlagPilot Platform                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       Frontend (Next.js + CopilotKit)                 │    │
│  │                 Auth · Chat UI · AG-UI Protocol Client                │    │
│  └─────────────────────────────────────┬───────────────────────────────┘    │
│                                      │ AG-UI Protocol                       │
│  ┌─────────────────────────────────────▼───────────────────────────────┐    │
│  │                    FastAPI Backend + CopilotKit SDK                  │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │             LangGraph Workflow + FlagPilot Orchestrator           │    │    │
│  │  └───────────────────────────┬─────────────────────────────────┘    │    │
│  │                              │                                      │    │
│  │  ┌───────────────────────────▼─────────────────────────────────┐    │    │
│  │  │                  MetaGPT Agent Pool (17 Agents)             │    │    │
│  │  │  Contract Guardian · Job Authenticator · Scope Sentinel ··· │    │    │
│  │  └───────────────────────────┬─────────────────────────────────┘    │    │
│  │                              │                                      │    │
│  │  ┌───────────────────────────▼─────────────────────────────────┐    │    │
│  │  │                     RAGFlow Integration                     │    │    │
│  │  │         Global Wisdom · Tiered Context Injection            │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          Infrastructure Layer                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │  Redis   │  │  MySQL   │  │  MinIO   │  │  Elastic │  │RAGFlow │  │   │
│  │  │  Cache   │  │(RAGFlow) │  │ Storage  │  │ Memory   │  │ Server │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │
│  │                         ┌────────────┐                               │   │
│  │                         │ PostgreSQL │                               │   │
│  │                         │ Auth/Users │                               │   │
│  │                         └────────────┘                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (v2.0+)
- **OpenRouter API Key** (for LLM access)
- **8GB+ RAM** recommended (ElasticSearch needs room)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FlagPilot.git
cd FlagPilot
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# ===========================================
# LLM Configuration (OpenRouter)
# ===========================================
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini

# ===========================================
# Redis (Cache)
# ===========================================
REDIS_PASSWORD=your-redis-password

# ===========================================
# RAGFlow Stack
# ===========================================
MYSQL_ROOT_PASSWORD=ragflow-root-pass
MYSQL_USER=ragflow
MYSQL_PASSWORD=ragflow-pass
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
RAGFLOW_ADMIN_EMAIL=admin@Flagpilot.ai
RAGFLOW_ADMIN_PASSWORD=admin123
```

### 3. Launch the Platform

```bash
docker compose up --build
```

### 4. Access the Services

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI + MetaGPT agents |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **RAGFlow UI** | http://localhost:9380 | Knowledge base management |
| **MinIO Console** | http://localhost:9001 | Object storage dashboard |

---

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ | - | Your OpenRouter API key |
| `OPENROUTER_MODEL` | ✅ | - | LLM model to use (e.g., `openai/gpt-4o-mini`) |
| `RAGFLOW_URL` | ❌ | `http://ragflow:80` | RAGFlow server URL |
| `REDIS_PASSWORD` | ✅ | - | Redis authentication password |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `RAGFLOW_API_KEY` | ❌ | - | RAGFlow API key (auto-configured) |

### Docker Services Overview

```yaml
services:
  backend:        # FastAPI + MetaGPT + CopilotKit (port 8000)
  redis:          # Session cache & pub/sub (port 6379)
  es01:           # Elasticsearch - FlagPilot memory system (port 9200)
  minio:          # Object storage for RAGFlow (ports 9000, 9001)
  mysql:          # RAGFlow internal database (NOT used by FlagPilot)
  ragflow:        # RAGFlow knowledge engine (port 9380)
  postgres:       # User auth & billing - frontend only (port 5432)
```

---

## 📚 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check with agent status |
| `GET` | `/api/agents` | List all registered agents |
| `POST` | `/api/team/chat` | Start a multi-agent workflow (SSE) |
| `POST` | `/api/rag/search` | Search the knowledge base |

### Example: Starting a Workflow

```bash
curl -X POST "http://localhost:8000/api/team/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Review this contract for red flags: [contract text]",
    "user_id": "user123"
  }'
```

### SSE Event Types

| Event | Description |
|-------|-------------|
| `message` | Text content from an agent |
| `agent_status` | Agent working/completed/error status |
| `workflow_update` | DAG visualization of the current plan |

> 📖 **For complete API documentation, see [backend/BACKEND_API.md](./backend/BACKEND_API.md)**

---

## 🧪 Verification & Testing Status

**Current Status (Dec 2025): ✅ STABLE - 17/17 Tests Passing**

The backend has passed a fully comprehensive live integration test suite.

**Report**: [View Full Test Report](backend/TEST_REPORT.md)

### Validated Features:
| Feature | Status | Tests |
|---------|--------|-------|
| LLM Integration | ✅ Verified | Contract Analysis & Negotiation |
| Elasticsearch Memory | ✅ Verified | 4 indices, 60+ CRUD ops |
| RAGFlow Search | ✅ Verified | Document Upload, Indexing, Retrieval |
| MetaGPT Orchestration | ✅ Verified | Full Team Introspection (Logs) |
| CopilotKit Integration | ✅ Verified | Agent Discovery & API |
| Scam Detection | ✅ Verified | Fast-Fail Logic |

### Run Tests Manually
```bash
# Run the unified live system test suite
docker exec Flagpilot-backend pytest tests/test_live_system.py -v

# Verbose with all LLM calls and responses
docker exec Flagpilot-backend pytest tests/test_live_system.py -v -s --log-cli-level=DEBUG

# All tests
docker exec Flagpilot-backend pytest tests/ -v
```

---

## 🛠️ Development

### Project Structure

```
Flag-Project/
├── backend/                    # FastAPI backend (Multi-Venv Architecture)
│   ├── agents/                 # MetaGPT agent definitions (17 agents)
│   ├── lib/
│   │   ├── memory/             # Elasticsearch Memory System
│   │   ├── copilotkit/         # CopilotKit SDK integration
│   │   └── runners/            # Subprocess runners for isolated venvs
│   ├── routers/                # API route handlers
│   ├── tests/                  # Test suites (32+ tests)
│   ├── requirements-*.txt      # Venv-specific dependencies
│   ├── Dockerfile              # Multi-venv container build
│   └── BACKEND_API.md          # API documentation
├── frontend/                   # Next.js frontend (CopilotKit)
├── docker-compose.yml          # Full stack orchestration
├── .env                        # Environment configuration
└── README.md                   # This file
```

### Local Development (Without Docker)

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Adding a New Agent

1. Create a new file in `backend/agents/roles/`:

```python
from agents.roles.base_role import FlagPilotRole

class MyNewAgent(FlagPilotRole):
    name: str = "my-new-agent"
    profile: str = "My Agent Description"
    goal: str = "What this agent accomplishes"
    
    # Agent implementation...
```

2. The agent will be **automatically discovered** by the registry on startup.

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style

- Python: Follow PEP 8, use type hints
- Commits: Use conventional commit messages
- Documentation: Update README and docstrings for new features

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ for Freelancers Everywhere</strong>
  <br>
  <em>Stop getting scammed. Start getting protected.</em>
</p>

<p align="center">
  <a href="https://github.com/yourusername/FlagPilot/issues">Report Bug</a>
  ·
  <a href="https://github.com/yourusername/FlagPilot/issues">Request Feature</a>
</p>
