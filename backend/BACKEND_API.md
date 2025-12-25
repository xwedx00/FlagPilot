# FlagPilot Backend API Documentation

## Multi-Venv Isolation Architecture

FlagPilot Backend uses a **4-environment isolation architecture** to ensure zero dependency conflicts between packages:

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Container                          │
├─────────────────────────────────────────────────────────────┤
│    CORE (/usr/local)          │  FastAPI, uvicorn, pydantic │
├─────────────────────────────────────────────────────────────┤
│    /opt/venv-copilotkit       │  copilotkit, langgraph      │
├─────────────────────────────────────────────────────────────┤
│    /opt/venv-metagpt          │  metagpt==0.8.1             │
├─────────────────────────────────────────────────────────────┤
│    /opt/venv-ragflow          │  ragflow-sdk, elasticsearch │
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

### RAG Operations
```
POST /api/v1/rag/ingest  # Ingest document from URL
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
| `ES_HOST` | Elasticsearch host |
| `ES_PORT` | Elasticsearch port (default: 9200) |

---

## Elasticsearch Memory System

The backend uses Elasticsearch for persistent memory management with 4 indices:

### Indices

| Index | Purpose |
|-------|---------|
| `flagpilot_user_profiles` | Dynamic user learning profiles |
| `flagpilot_chat_history` | Conversation logs with session tracking |
| `flagpilot_experience_gallery` | Shared learnings from successful interactions |
| `flagpilot_global_wisdom` | Aggregated insights across all users |

### Features

1. **Dynamic User Profiles**
   - Auto-learns from interactions
   - LLM-powered profile synthesis
   - Preferences and behavior patterns

2. **Chat History**
   - Complete conversation storage
   - Session-based organization
   - Agent-tagged messages

3. **Global Wisdom**
   - Anonymized best practices
   - Confidence scoring
   - Category-based search

4. **Experience Gallery**
   - Successful interaction examples
   - Similar case search
   - Feedback scoring

### Usage (in code)
```python
from lib.memory.manager import get_memory_manager

manager = get_memory_manager()

# User profiles
profile = await manager.get_user_profile("user123")
await manager.update_user_profile("user123", summary="...")

# Chat history
await manager.save_chat("user123", "user", "Help with contract")
history = await manager.get_chat_history("user123")

# Global wisdom
await manager.add_wisdom("contract", "Always get deposits")
wisdom = await manager.get_global_wisdom(category="contract")
```

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
│   ├── memory/                # Elasticsearch Memory System
│   │   └── manager.py         # MemoryManager class
│   └── runners/               # Subprocess runners for venvs
│       ├── copilotkit_runner.py
│       ├── metagpt_runner.py
│       └── ragflow_runner.py
├── agents/                    # MetaGPT agent definitions
├── routers/                   # FastAPI routers
└── Dockerfile                 # Multi-venv build
```
