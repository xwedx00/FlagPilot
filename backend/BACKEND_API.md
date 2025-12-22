# FlagPilot Backend API Documentation

## Multi-Venv Isolation Architecture

FlagPilot Backend uses a **4-environment isolation architecture** to ensure zero dependency conflicts between packages:

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Container                          │
├─────────────────────────────────────────────────────────────┤
│    CORE (/usr/local)          │  FastAPI, uvicorn, pydantic │
├─────────────────────────────────────────────────────────────┤
│    venv-copilotkit            │  copilotkit, langgraph      │
├─────────────────────────────────────────────────────────────┤
│    venv-metagpt               │  metagpt==0.8.1             │
├─────────────────────────────────────────────────────────────┤
│    venv-ragflow               │  ragflow-sdk, elasticsearch │
└─────────────────────────────────────────────────────────────┘
```

### Benefits
- **Zero conflicts**: Each SDK manages its own dependencies
- **Future-proof**: No dependency pinning needed (except MetaGPT 0.8.1)
- **Easy upgrades**: Update any venv independently

---

## API Endpoints

### Health Check
```
GET /health
```
Returns server status, agents list, and version.

### CopilotKit Integration
```
POST /copilotkit
```
Primary frontend integration endpoint. CopilotKit SDK handles streaming.

### Agents
```
GET /api/agents          # List all agents
GET /api/agents/{id}     # Get agent details
```

### RAG Search
```
POST /api/rag/search     # Search knowledge base
```

---

## Agent List (15 Specialists)

| ID | Name | Purpose |
|----|------|---------|
| contract-guardian | Contract Guardian | Legal contract analysis |
| job-authenticator | Job Authenticator | Scam detection |
| scope-sentinel | Scope Sentinel | Scope creep prevention |
| payment-enforcer | Payment Enforcer | Payment recovery |
| dispute-mediator | Dispute Mediator | Conflict resolution |
| communication-coach | Communication Coach | Professional messaging |
| negotiation-assistant | Negotiation Assistant | Rate negotiation |
| profile-analyzer | Profile Analyzer | Profile optimization |
| ghosting-shield | Ghosting Shield | Client ghosting recovery |
| risk-advisor | Risk Advisor | Risk assessment |
| talent-vet | Talent Vet | Candidate evaluation |
| application-filter | Application Filter | Job filtering |
| feedback-loop | Feedback Loop | Continuous improvement |
| planner-role | Planner Role | Workflow planning |
| flagpilot-orchestrator | Orchestrator | Multi-agent coordination |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_MODEL` | Model to use (e.g., anthropic/claude-3.5-sonnet) |
| `RAGFLOW_URL` | RAGFlow server URL |
| `RAGFLOW_API_KEY` | RAGFlow API key |
| `REDIS_URL` | Redis connection string |

---

## File Structure

```
backend/
├── requirements-core.txt       # FastAPI, uvicorn, pydantic
├── requirements-copilotkit.txt # copilotkit, langgraph
├── requirements-metagpt.txt    # metagpt==0.8.1
├── requirements-ragflow.txt    # ragflow-sdk
├── lib/
│   ├── copilotkit/            # CopilotKit SDK integration
│   │   ├── graph.py           # LangGraph workflow
│   │   └── sdk.py             # SDK setup
│   └── runners/               # Subprocess runners for venvs
│       ├── copilotkit_runner.py
│       ├── metagpt_runner.py
│       └── ragflow_runner.py
├── agents/                    # MetaGPT agent definitions
├── routers/                   # FastAPI routers
└── Dockerfile                 # Multi-venv build
```
