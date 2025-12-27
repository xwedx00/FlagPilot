<p align="center">
  <img src="https://img.shields.io/badge/FlagPilot-AI%20Agent%20Platform-6366F1?style=for-the-badge&logo=robot&logoColor=white" alt="FlagPilot">
</p>

<h1 align="center">🚀 FlagPilot v6.1</h1>

<p align="center">
  <strong>Enterprise-Grade AI Protection for Freelancers</strong>
  <br>
  <em>17 specialized LangGraph AI agents orchestrated to protect your freelance career</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-6.1.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B6B?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/CopilotKit-AG--UI-4ECDC4?style=flat-square&logo=react&logoColor=white" alt="CopilotKit">
  <img src="https://img.shields.io/badge/PostgreSQL-Persistent-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
</p>

---

## 🎯 What is FlagPilot?

**FlagPilot** is an enterprise-grade AI platform designed specifically for freelancers. Built on **LangGraph** and **LangChain** with **RAGFlow** knowledge retrieval, it orchestrates 17 specialized AI agents that work together to:

| Capability | Description |
|------------|-------------|
| 📜 **Contract Analysis** | Detect legal risks, unfavorable clauses, missing protections |
| 🔍 **Scam Detection** | Fast-fail protection with 5+ scam signal patterns |
| 🎯 **Scope Creep Prevention** | Identify boundary violations before they escalate |
| 💰 **Payment Enforcement** | Collection strategies and late fee policies |
| 🤝 **Negotiation Assistance** | Rate benchmarking and counter-offer strategies |
| 🧠 **Learning Memory** | Global wisdom database + personal experience gallery |

> 💡 **Think of FlagPilot as your personal team of AI advisors**—a lawyer, a fraud investigator, a negotiator, and more—all working 24/7 to protect your freelance career.

---

## ✨ Key Features

### 🚨 Fast-Fail Risk Detection
```
User Input → Scam Signals Check → CRITICAL RISK? → Immediate Risk Advisor
                                       ↓ Safe
                              Normal Agent Processing
```
When **ANY** agent detects a critical risk (scam pattern, unenforceable contract, known bad actor), the entire workflow **immediately halts** and a specialized `RiskAdvisor` provides emergency protocols.

### 🧠 LLM Router (Intelligent Agent Selection)
Unlike keyword matching, our LLM Router analyzes task semantics:
- **Confidence scoring** for each agent selection
- **Urgency detection** (low/medium/high/critical)
- **Fallback routing** to planner when uncertain

### 💾 Persistent State (PostgreSQL)
```
AsyncPostgresSaver → checkpoints table → Survives Docker restarts
PostgresStore      → long_term_memory → Cross-thread preferences
Elasticsearch      → wisdom/profiles  → Searchable knowledge base
```

### 🎮 Command Palette (⌘K)
Quick access to all agents and actions:
- 6 agent shortcuts with descriptions
- 4 quick actions (memory, search, export, clear)
- GSAP animations for premium feel

### 📊 Real-Time Streaming
CopilotKit AG-UI protocol for live agent responses with state synchronization.

### 📈 LangSmith Observability
Full tracing of agent executions, token usage, and performance metrics.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           FLAGPILOT v6.1 ARCHITECTURE                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              FRONTEND LAYER                                 │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐   │ │
│  │  │    Next.js 15     │  │   CopilotKit UI   │  │   Shadcn + GSAP       │   │ │
│  │  │    App Router     │  │   AG-UI Protocol  │  │   Premium Animations  │   │ │
│  │  │    TypeScript     │  │   Real-time SSE   │  │   Command Palette ⌘K  │   │ │
│  │  └───────────────────┘  └───────────────────┘  └───────────────────────┘   │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐   │ │
│  │  │   Better Auth     │  │   Drizzle ORM     │  │   Memory Panel UI     │   │ │
│  │  │   OAuth (GitHub)  │  │   PostgreSQL      │  │   Risk Alert Display  │   │ │
│  │  └───────────────────┘  └───────────────────┘  └───────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              BACKEND LAYER                                  │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                         FastAPI Application                           │  │ │
│  │  │  /copilotkit (AG-UI) │ /api/agents │ /api/memory │ /api/v1/rag       │  │ │
│  │  └───────────────────────────────────────────────────────────────────────┘  │ │
│  │                                        │                                     │ │
│  │                                        ▼                                     │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                          LLM ROUTER                                   │  │ │
│  │  │    ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐     │  │ │
│  │  │    │  Semantic   │───▶│ Confidence  │───▶│   Urgency Level     │     │  │ │
│  │  │    │  Analysis   │    │   Scoring   │    │   Detection         │     │  │ │
│  │  │    └─────────────┘    └─────────────┘    └─────────────────────┘     │  │ │
│  │  └───────────────────────────────────────────────────────────────────────┘  │ │
│  │                                        │                                     │ │
│  │                                        ▼                                     │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                     LANGGRAPH ORCHESTRATOR                            │  │ │
│  │  │  ┌─────────────┐   ┌─────────────────┐   ┌───────────────────────┐   │  │ │
│  │  │  │    PLAN     │──▶│     EXECUTE     │──▶│      SYNTHESIZE       │   │  │ │
│  │  │  │    NODE     │   │     AGENTS      │   │    (LLM Summary)      │   │  │ │
│  │  │  │             │   │   (Parallel)    │   │                       │   │  │ │
│  │  │  └─────────────┘   └─────────────────┘   └───────────────────────┘   │  │ │
│  │  │                             │                                         │  │ │
│  │  │                             ▼                                         │  │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │                   17 SPECIALIST AGENTS                        │   │  │ │
│  │  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │   │  │ │
│  │  │  │  │  Contract   │ │    Job      │ │    Risk     │ │  Scope  │ │   │  │ │
│  │  │  │  │  Guardian   │ │  Authent.   │ │   Advisor   │ │ Sentinel│ │   │  │ │
│  │  │  │  │  ⚖️ Legal   │ │ 🔍 Scam     │ │ 🚨 Critical │ │ 🎯 Scope│ │   │  │ │
│  │  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │   │  │ │
│  │  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │   │  │ │
│  │  │  │  │  Payment    │ │ Negotiation │ │   Comms     │ │ Dispute │ │   │  │ │
│  │  │  │  │  Enforcer   │ │  Assistant  │ │   Coach     │ │ Mediator│ │   │  │ │
│  │  │  │  │ 💰 Collect  │ │ 🤝 Rate     │ │ 💬 Message  │ │ ⚔️ Resolve│ │   │  │ │
│  │  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │   │  │ │
│  │  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │   │  │ │
│  │  │  │  │  Ghosting   │ │   Profile   │ │   Talent    │ │   App   │ │   │  │ │
│  │  │  │  │   Shield    │ │  Analyzer   │ │    Vet      │ │ Filter  │ │   │  │ │
│  │  │  │  │ 👻 Re-engage│ │ 📊 Vet      │ │ 🎓 Evaluate │ │ 📝 Screen│ │   │  │ │
│  │  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │   │  │ │
│  │  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │   │  │ │
│  │  │  │  │  Feedback   │ │   Planner   │ │  + 3 More   │             │   │  │ │
│  │  │  │  │    Loop     │ │    Role     │ │   Agents    │             │   │  │ │
│  │  │  │  │ 🔄 Learn    │ │ 📋 Organize │ │             │             │   │  │ │
│  │  │  │  └─────────────┘ └─────────────┘ └─────────────┘             │   │  │ │
│  │  │  └───────────────────────────────────────────────────────────────┘   │  │ │
│  │  └───────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           PERSISTENCE LAYER                                 │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐   │ │
│  │  │    PostgreSQL     │  │   Elasticsearch   │  │       Redis           │   │ │
│  │  │  ┌─────────────┐  │  │  ┌─────────────┐  │  │  ┌─────────────────┐  │   │ │
│  │  │  │ Checkpoints │  │  │  │   Wisdom    │  │  │  │   Session Cache │  │   │ │
│  │  │  │ Long-term   │  │  │  │  Profiles   │  │  │  │   Rate Limiting │  │   │ │
│  │  │  │ Memory      │  │  │  │  Chat Logs  │  │  │  │                 │  │   │ │
│  │  │  │ User Auth   │  │  │  │ Experience  │  │  │  │                 │  │   │ │
│  │  │  └─────────────┘  │  │  └─────────────┘  │  │  └─────────────────┘  │   │ │
│  │  └───────────────────┘  └───────────────────┘  └───────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           EXTERNAL SERVICES                                 │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐   │ │
│  │  │     RAGFlow       │  │    OpenRouter     │  │      LangSmith        │   │ │
│  │  │  Knowledge Base   │  │   LLM Provider    │  │    Observability      │   │ │
│  │  │  Document RAG     │  │   Claude/GPT-4    │  │   Tracing/Metrics     │   │ │
│  │  └───────────────────┘  └───────────────────┘  └───────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Agent Roster (17 Agents)

### Protection Agents
| Agent | Role | Specialization | Fast-Fail |
|-------|------|----------------|-----------|
| ⚖️ **Contract Guardian** | Legal Analyst | Risk clauses, IP terms, payment terms | ❌ |
| 🔍 **Job Authenticator** | Scam Detective | Scam patterns, red flags, verification | ✅ |
| 🚨 **Risk Advisor** | Emergency Override | Critical warnings, immediate actions | ✅ |
| 🎯 **Scope Sentinel** | Scope Protector | Scope creep, change orders, boundaries | ❌ |

### Business Agents
| Agent | Role | Specialization |
|-------|------|----------------|
| 💰 **Payment Enforcer** | Collection Specialist | Late fees, invoices, collection strategies |
| 🤝 **Negotiation Assistant** | Deal Maker | Rate benchmarking, counter-offers, value framing |
| 💬 **Communication Coach** | Messaging Expert | Professional responses, difficult conversations |
| ⚔️ **Dispute Mediator** | Conflict Resolver | Escalation paths, resolution strategies |

### Intelligence Agents
| Agent | Role | Specialization |
|-------|------|----------------|
| 👻 **Ghosting Shield** | Client Tracker | Re-engagement, follow-up sequences |
| 📊 **Profile Analyzer** | Client Vetter | Background research, risk scoring |
| 🎓 **Talent Vet** | Candidate Evaluator | Collaborator evaluation, skills verification |
| 📝 **Application Filter** | Job Matcher | Spam detection, AI-generated content detection |
| 🔄 **Feedback Loop** | Learning Engine | Outcome tracking, recommendation improvement |
| 📋 **Planner Role** | Task Organizer | Complex task breakdown, multi-step planning |

---

## 🎨 Frontend Features

| Feature | Description | Technology |
|---------|-------------|------------|
| **Real-time Chat** | Streaming AI responses with typing indicators | CopilotKit AG-UI |
| **Command Palette** | ⌘K for quick agent access and actions | Shadcn Command + GSAP |
| **Memory Panel** | View wisdom, profiles, and chat history | Elasticsearch API |
| **Risk Alerts** | Visual warnings for critical detections | AI-controlled via CopilotKit |
| **Dark Mode** | Premium dark theme with glassmorphism | Tailwind CSS 4 |
| **OAuth Login** | GitHub and Google authentication | Better Auth |
| **Agent Status** | Live "17 Agents Ready" indicator | WebSocket sync |

---

## 🔧 Backend Features

| Feature | Description | Technology |
|---------|-------------|------------|
| **Multi-Agent Orchestration** | Parallel agent execution with synthesis | LangGraph |
| **LLM Router** | Semantic task analysis for agent selection | LangChain + OpenRouter |
| **Persistent State** | Conversation history survives restarts | AsyncPostgresSaver |
| **Long-term Memory** | Cross-session user preferences | PostgresStore |
| **Global Wisdom** | Community knowledge database | Elasticsearch |
| **RAG Integration** | Document search and context injection | RAGFlow |
| **Fast-Fail Detection** | Programmatic scam signal detection | Custom algorithms |
| **Observability** | Full agent tracing and metrics | LangSmith |
| **Rate Limiting** | Tier-based API throttling | Redis |

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

# Database (for persistent state)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/flagpilot

# Optional but Recommended
LANGSMITH_API_KEY=lsv2_pt_your-key
RAGFLOW_API_KEY=your-ragflow-key
```

### 3. Start with Docker

```bash
docker-compose up -d
```

### 4. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| RAGFlow | http://localhost:9380 |

---

## ⚙️ Configuration Reference

### Required Variables
| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access |
| `OPENROUTER_MODEL` | Model ID (e.g., `anthropic/claude-3.5-sonnet`) |

### Database & Persistence
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | *(none - uses memory)* |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `ES_HOST` | Elasticsearch host | `es01` |
| `ES_PORT` | Elasticsearch port | `9200` |

### Observability
| Variable | Description | Default |
|----------|-------------|---------|
| `LANGSMITH_API_KEY` | LangSmith API key | *(optional)* |
| `LANGSMITH_PROJECT` | Project name for traces | `flagpilot` |

### RAGFlow
| Variable | Description | Default |
|----------|-------------|---------|
| `RAGFLOW_URL` | RAGFlow server URL | `http://ragflow:80` |
| `RAGFLOW_API_KEY` | RAGFlow API key | *(optional)* |

---

## 🧪 Testing

```bash
# Smart-Stack feature tests (fast)
docker exec Flagpilot-backend python tests/test_smart_stack.py

# Full integration tests (comprehensive)
docker exec Flagpilot-backend python -m pytest tests/test_live_system.py -v -s

# View detailed output
docker exec Flagpilot-backend cat test_live_output.txt
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Backend README](backend/README.md) | Architecture, directory structure, API |
| [API Reference](backend/BACKEND_API.md) | Endpoint documentation |
| [Test Report](backend/TEST_REPORT.md) | Latest test results |
| [Frontend README](frontend/README.md) | UI components, CopilotKit setup |

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Agent Framework | LangGraph + LangChain |
| LLM Provider | OpenRouter |
| State Persistence | AsyncPostgresSaver |
| Long-term Memory | PostgresStore |
| Search/Memory | Elasticsearch 9.0 |
| Knowledge Base | RAGFlow |
| Cache | Redis |
| Observability | LangSmith |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| UI Library | Shadcn UI |
| Styling | Tailwind CSS 4 |
| Animations | GSAP |
| AI Integration | CopilotKit AG-UI |
| Authentication | Better Auth |
| Database ORM | Drizzle ORM |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Container | Docker Compose |
| Database | PostgreSQL 15 |
| Search | Elasticsearch 9.0 |
| Cache | Redis |
| Object Storage | MinIO |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with ❤️ for freelancers worldwide</strong>
</p>
