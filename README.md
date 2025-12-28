# FlagPilot v7.0 (Enterprise Edition)

![Next.js 16](https://img.shields.io/badge/Next.js-16.1-black?style=for-the-badge&logo=next.js)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestrator-orange?style=for-the-badge)
![CopilotKit](https://img.shields.io/badge/CopilotKit-AG--UI-purple?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)

## 🛡️ The AI-Native Freelancer Protection Platform

FlagPilot is an enterprise-grade protection suite for freelancers. It orchestrates **14 specialized AI agents** to detect scams, analyze legal contracts, negotiate rates, and resolve disputes. 

Unlike simple "wrappers", FlagPilot uses a **hybrid architecture**: a Next.js 16 frontend that acts as a "Headless Host" for a powerful Python/LangGraph backend, communicating via the **CopilotKit AG-UI Protocol**. This ensures real-time state streaming, critical risk "fast-fail" mechanisms, and persistent memory across sessions.

### The Smart Stack

| Layer | Technology | Key Role |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 16.1** (App Router) | UI, Auth (Better-Auth), GSAP Animations |
| **Protocol** | **CopilotKit** (AG-UI) | Tunnels UI Actions (`toggleMemory`) to Backend Agents |
| **Backend** | **FastAPI** + **LangGraph** | Multi-Agent Orchestration, State Management |
| **Intelligence**| **OpenRouter** (LLM) | Model Agnostic Intelligence (GPT-4, Claude 3.5) |
| **Memory** | **Elasticsearch** | Triple-Store: User Profiles, Chat History, Global Wisdom |
| **Vector DB** | **Qdrant** | RAG Knowledge Base (Contracts, Laws, Best Practices) |
| **Storage** | **MinIO** | S3-Compatible Object Storage for Documents |
| **Persistence** | **PostgreSQL** | LangGraph Checkpoints & User Sessions |

---

## 🏗️ The Grand Architecture

```ascii
+-------------------------------------------------------------+
|                     USER (Freelancer)                       |
+------------------------------+------------------------------+
                               |
                               v
+------------------------------+------------------------------+
|                   FRONTEND (Next.js 16)                     |
|                                                             |
|  [Command Palette]    [Chat Interface]    [Memory Panel]    |
|          |                   |                   |          |
|      (GSAP)        (<CopilotKit Provider>)       |          |
+------------------------------+------------------------------+
                               |
                   (CopilotKit AG-UI Protocol)
               JSON Patches / SSE Stream / Actions
                               |
                               v
+------------------------------+------------------------------+
|                    BACKEND (FastAPI)                        |
|                                                             |
|   [Auth Middleware] -> [ /copilotkit Endpoint ]             |
|                                |                            |
|                        (LangGraph Graph)                    |
|                                |                            |
|   +----------------------------+------------------------+   |
|   |                 ORCHESTRATOR NODE                   |   |
|   |  (Scam Detection -> Context Injection -> Routing)   |   |
|   +----------------------------+------------------------+   |
|                                |                            |
|                  +-------------+-------------+              |
|                  |             |             |              |
|        [Legal Agents]   [Finance Agents] [Risk Agents]      |
|                                |                            |
+----------------+---------------+----------------------------+
                 |               |
        +--------+-------+   +---+---+
        | DATA LAYER     |   | TOOLS |
        +----------------+   +-------+
        | Postgres (DB)  |---| RAG Pipeline (Qdrant)
        | Elastic (Mem)  |---| Storage (MinIO)
        | Redis (Cache)  |---| Search Tools
        +----------------+   +-----------------------+
```

---

## 🤖 Agent Roster (The Brains)

The system is powered by **14 Specialist Agents** (`backend/agents/`), expertly routed by an LLM-based Router.

### 🛡️ Protection & Risk
*   **Contract Guardian**: Analyzes legal contracts for unfair terms and IP risks.
*   **Job Authenticator**: Detects scam patterns in job postings (Fast-Fail enabled).
*   **Risk Advisor**: Emergency protocols for critical threats (Fraud, Phishing).
*   **Scope Sentinel**: Detects scope creep and boundary violations.

### 💰 Finance & Business
*   **Payment Enforcer**: Tracks invoices and generates collection strategies.
*   **Negotiation Assistant**: market rate benchmarking and counter-offer scripts.
*   **Application Filter**: Screens and prioritizes job opportunities.
*   **Profile Analyzer**: Vets potential clients for reputation risks.

### 🗣️ Communication & Strategy
*   **Communication Coach**: Drafts professional emails and proposals.
*   **Dispute Mediator**: Conflict resolution strategies and evidence assessment.
*   **Ghosting Shield**: Re-engagement campaigns for unresponsive clients.
*   **Talent Vet**: Evaluates potential subcontractors/collaborators.
*   **Planner Role**: Breaks down complex projects into actionable steps.
*   **Feedback Loop**: Learns from outcomes to improve system recommendations.

---

## 🗺️ Unified Directory Map

```text
Flag-Project/
├── docker-compose.yml          # The Glue. Orchestrates all 7 services.
├── .env.example                # The Config. Single source of truth for secrets.
├── frontend/                   # Next.js 16 App
│   ├── app/layout.tsx          # CopilotKit Provider setup
│   ├── components/chat/        # Chat Interface & Command Palette
│   └── lib/hooks/              # Custom Actions (useFlagPilotActions)
└── backend/                    # FastAPI App
    ├── main.py                 # Entry Point
    ├── agents/                 # The 14 Agents & Router Logic
    ├── lib/
    │   ├── auth/               # Postgres-backed Session Validation
    │   ├── memory/             # Elasticsearch Manager
    │   └── persistence/        # AsyncPostgresSaver (Checkpointer)
    └── routers/                # API Endpoints (RAG, Health)
```

---

## 🚀 "It Just Works" Setup Guide

### Prerequisites
*   **Docker & Docker Compose** (Desktop or Engine)
*   **Git**

### Step 1: Clone & Configure
```bash
git clone https://github.com/your-org/flagpilot.git
cd flagpilot

# Set up environment variables
# Copy .env.example to .env and fill in:
# - OPENROUTER_API_KEY (Required for AI)
# - DATABASE_URL, etc. (Defaults work for Docker)
cp .env.example .env
```

### Step 2: Launch the Stack
This spins up the entire enterprise infrastructure:
```bash
docker-compose up --build -d
```

### Step 3: Access Services
| Service | URL | Credentials (Default) |
| :--- | :--- | :--- |
| **Frontend UI** | `http://localhost:3000` | User Mode |
| **Backend API** | `http://localhost:8000` | - |
| **API Docs** | `http://localhost:8000/docs` | Swagger UI |
| **MinIO Console**| `http://localhost:9001` | `minioadmin` / `minioadmin` |
| **Qdrant UI** | `http://localhost:6333` | - |
| **Mailpit** | `http://localhost:8025` | (If enabled) |

### Troubleshooting
*   **"Checkpointer Error"**: Ensure Postgres is healthy (`docker-compose ps`). The backend needs it for LangGraph persistence.
*   **"Copilot Connection Failed"**: Check if `BACKEND_COPILOT_URL` in frontend `.env` matches the docker network or localhost mapping.
*   **"Qdrant/MinIO Connection"**: The backend service uses internal docker DNS (`qdrant`, `minio`). If running backend *locally* (outside Docker), update `.env` to use `localhost`.
