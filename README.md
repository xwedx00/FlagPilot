<p align="center">
  <img src="https://img.shields.io/badge/FlagPilot-AI%20Agent%20Platform-6366F1?style=for-the-badge&logo=robot&logoColor=white" alt="FlagPilot">
</p>

<h1 align="center">🚀 FlagPilot v6.1</h1>

<p align="center">
  <strong>Your AI-Powered Freelancer Protection Platform</strong>
  <br>
  <em>17 specialized LangGraph AI agents working together to protect you from bad clients, scams, and scope creep</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-00CED1?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B6B?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/CopilotKit-AG--UI-4ECDC4?style=flat-square&logo=react&logoColor=white" alt="CopilotKit">
  <img src="https://img.shields.io/badge/PostgreSQL-Persistent-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
</p>

---

## 🎯 What is FlagPilot?

**FlagPilot** is an intelligent AI platform designed specifically for freelancers. Built on **LangGraph** and **LangChain** with **RAGFlow** knowledge retrieval, it orchestrates a team of 17 specialized AI agents that work together to:

- **Analyze contracts** for legal risks and unfavorable terms
- **Detect scams** and verify job leads before you commit
- **Identify scope creep** before it happens
- **Provide legal guidance** and negotiation strategies
- **Learn from a global database** of successful freelance strategies
- **Remember your preferences** across sessions with persistent memory

> 💡 **Think of FlagPilot as your personal team of AI advisors**—a lawyer, a fraud investigator, a negotiator, and more—all working 24/7 to protect your freelance career.

---

## ✨ Key Features

### 🚨 Fast-Fail Risk Detection
When **ANY** agent detects a critical risk (scam pattern, unenforceable contract, known bad actor), the entire workflow **immediately halts**. A specialized `RiskAdvisor` is dynamically injected to provide emergency protocols and safety guidance.

### 🧠 LLM Router (NEW in v6.1)
Intelligent semantic agent selection using LLM analysis. Replaces keyword matching with proper task understanding, confidence scoring, and urgency detection.

### 💾 Persistent State (NEW in v6.1)
Sessions survive Docker restarts! AsyncPostgresSaver keeps your conversation history and agent state persistent in PostgreSQL.

### 🎮 Command Palette
Press `⌘K` to quickly access agents and actions. AI can also control UI elements like the memory panel and risk alerts.

### 📊 Real-Time Streaming
Watch your AI team work in real-time with CopilotKit AG-UI protocol streaming.

### 📈 LangSmith Observability
Full tracing and evaluation of agent performance with LangSmith integration.

---

## 🤖 AI Agent Roster (17 Agents)

| Agent | Role | Description |
|-------|------|-------------|
| ⚖️ **Contract Guardian** | Legal Analyst | Analyzes contracts for risks and unfavorable clauses |
| 🔍 **Job Authenticator** | Scam Detective | Detects scam patterns with Fast-Fail capability |
| 🚨 **Risk Advisor** | Emergency Override | Provides critical safety protocols |
| 🎯 **Scope Sentinel** | Scope Protector | Identifies scope creep indicators |
| 💰 **Payment Enforcer** | Payment Protector | Ensures fair, enforceable payment terms |
| 🤝 **Negotiation Assistant** | Deal Maker | Provides negotiation strategies |
| 💬 **Communication Coach** | Messaging Expert | Crafts professional responses |
| ⚔️ **Dispute Mediator** | Conflict Resolver | Guides dispute resolution |
| 👻 **Ghosting Shield** | Client Tracker | Provides follow-up strategies |
| 📊 **Profile Analyzer** | Client Vetter | Analyzes client profiles |
| 🎓 **Talent Vet** | Candidate Evaluator | Evaluates collaborators |
| 📝 **Application Filter** | Job Matcher | Filters applications |
| 🔄 **Feedback Loop** | Learning Engine | Improves recommendations |
| 📋 **Planner Role** | Task Organizer | Plans complex workflows |
| *+ 3 additional specialized agents* | | |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FlagPilot v6.1                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────────────────────┐ │
│  │   Next.js   │←──→│      CopilotKit Frontend            │ │
│  │   Frontend  │    │   (AG-UI + Command Palette ⌘K)      │ │
│  └─────────────┘    └─────────────────────────────────────┘ │
│         ↕                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  FastAPI Backend                        │ │
│  │  ┌───────────────────────────────────────────────────┐  │ │
│  │  │         LLM Router (Semantic Selection)           │  │ │
│  │  └───────────────────────────────────────────────────┘  │ │
│  │                         ↓                               │ │
│  │  ┌───────────────────────────────────────────────────┐  │ │
│  │  │           LangGraph Orchestrator                  │  │ │
│  │  │   Plan → Execute (17 Agents) → Synthesize         │  │ │
│  │  └───────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│         ↕                    ↕                    ↕          │
│  ┌───────────┐    ┌─────────────────┐    ┌──────────────┐   │
│  │ PostgreSQL│    │  Elasticsearch  │    │  LangSmith   │   │
│  │(Persistent)│    │    (Memory)     │    │(Observability)│  │
│  └───────────┘    └─────────────────┘    └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

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
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=kwaipilot/kat-coder-pro:free

# Recommended (for persistent state)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/flagpilot

# Optional
LANGSMITH_API_KEY=your-langsmith-key
RAGFLOW_API_KEY=your-ragflow-key
```

### 3. Start with Docker

```bash
docker-compose up -d
```

### 4. Access

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key for LLM |
| `OPENROUTER_MODEL` | ✅ | Model to use |
| `DATABASE_URL` | ⭐ | PostgreSQL for persistent state |
| `LANGSMITH_API_KEY` | ❌ | LangSmith for observability |
| `RAGFLOW_URL` | ❌ | RAGFlow endpoint |
| `RAGFLOW_API_KEY` | ❌ | RAGFlow API key |
| `ES_HOST` | ❌ | Elasticsearch host |
| `REDIS_URL` | ❌ | Redis cache URL |

---

## 🧪 Testing

```bash
# Run Smart-Stack feature tests
docker exec Flagpilot-backend python tests/test_smart_stack.py

# Run live integration tests
docker exec Flagpilot-backend python -m pytest tests/test_live_system.py -v -s

# View output
docker exec Flagpilot-backend cat test_live_output.txt
```

---

## 📚 Documentation

- [Backend README](backend/README.md) - Architecture details
- [API Reference](backend/BACKEND_API.md) - Endpoint documentation
- [Test Report](backend/TEST_REPORT.md) - Test results

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | LangGraph + LangChain |
| LLM | OpenRouter (Claude, GPT-4, etc.) |
| State Persistence | AsyncPostgresSaver (PostgreSQL) |
| Frontend Integration | CopilotKit AG-UI |
| Knowledge Base | RAGFlow |
| Memory | Elasticsearch |
| Observability | LangSmith |
| Backend | FastAPI |
| Frontend | Next.js 15 |
| Cache | Redis |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
