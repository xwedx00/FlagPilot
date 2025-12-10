# FlagPilot Backend 🚀

The intelligent core of FlagPilot, built with **FastAPI**, **MetaGPT**, and **RAGFlow**.

FlagPilot is an AI-driven platform that protects freelancers from bad clients, scams, and scope creep. It orchestrates a team of specialized AI agents to analyze contracts, verify job leads, and provide legal/strategic advice using a "Global Wisdom" database.

## 🏗 Architecture

-   **Orchestrator Agency**: Uses the `FlagPilotOrchestrator` to dynamically plan and assign tasks to specialized agents.
-   **Agents**:
    -   `ContractGuardian`: Legal analysis.
    -   `JobAuthenticator`: Scam detection (with Fast-Fail).
    -   `ScopeSentinel`: Scope creep detection.
    -   `RiskAdvisor`: Emergency guidance override.
    -   ...and many more.
-   **RAG Engine (RAGFlow)**:
    -   **Global Wisdom**: Shared database of successful freelance strategies.
    -   **Tiered Context**: Injects specific RAG documents into specific agents based on the Orchestrator's plan.
-   **Fast-Fail Mechanism**:
    -   If ANY agent detects `CRITICAL_RISK` (e.g., a known scam pattern), the workflow aborts immediately.
    -   A `RiskAdvisor` is dynamically injected to give emergency safety protocols.
-   **Persistence**:
    -   All workflow executions are saved to a PostgreSQL database via SQLAlchemy (`WorkflowExecution` model).

## 🚀 Setup & Run

### Prerequisites
-   Docker & Docker Compose
-   OpenRouter API Key

### Configuration
Create a `.env` file in this directory (see `.env.example`):
```env
OPENROUTER_API_KEY=sk-...
OPENROUTER_MODEL=openai/gpt-oss-120b:free
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/flagpilot
```

### Run with Docker
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## 📚 API Documentation
For detailed API endpoints, schemas, and frontend integration guides, see **[BACKEND_API.md](./BACKEND_API.md)**.

## 🧪 Testing
The backend includes a comprehensive Stress Test Suite verifying Global Wisdom retrieval, Agent orchestration, and Fast-Fail logic.

```bash
docker exec flagpilot-backend python -m pytest tests/test_stress_global_wisdom.py
```

## 🛠 Features

### 1. Robustness "Fast-Fail"
Standardized Risk Schema across agents. The system monitors for `is_critical_risk: true`. If triggered, it cancels pending tasks and prioritizes user safety.

### 2. Global Wisdom RAG
Agents don't just "guess". They retrieve 5-star rated strategies ("Wisdom") from the RAGFlow database and apply them to the user's situation.

### 3. Workflow Persistence
Every interaction is saved. Users can retrieve past plans and agent advice via the History API.
