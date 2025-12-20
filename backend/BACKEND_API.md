# FlagPilot Backend API - AG-UI Protocol

## Overview

FlagPilot backend implements the **AG-UI (Agent-User Interaction) Protocol** for real-time communication between the multi-agent system and frontends.

**Protocol Reference**: https://docs.ag-ui.com/

## Base URL
```
http://localhost:8000
```

## AG-UI Protocol Endpoints

### POST `/api/agui` (Main Endpoint)
### POST `/api/team/chat` (Alias)

**Description**: Multi-agent team orchestration using AG-UI protocol.

**Request Body** (RunAgentInput):
```json
{
  "thread_id": "optional-uuid",
  "run_id": "optional-uuid",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Review this freelance contract for red flags"
    }
  ],
  "tools": [],
  "context": [
    {"type": "user_id", "value": "user-123"}
  ],
  "state": {},
  "agents": ["contract-guardian"]
}
```

**Response**: SSE stream of AG-UI events

---

### POST `/api/agents/{agent_id}/chat`

**Description**: Chat with a single specific agent.

**Path Parameters**:
- `agent_id`: Agent identifier (e.g., `contract-guardian`, `job-authenticator`)

**Request Body**: Same as `/api/agui`

---

### GET `/api/agents`

**Description**: List all available agents.

**Response**:
```json
{
  "agents": [
    {"id": "contract-guardian", "name": "contract-guardian", "description": "..."},
    {"id": "job-authenticator", "name": "job-authenticator", "description": "..."}
  ],
  "count": 17
}
```

---

## AG-UI Event Types

The backend emits these standard AG-UI events:

### Lifecycle Events
| Event | Description |
|-------|-------------|
| `RUN_STARTED` | Agent run has begun |
| `RUN_FINISHED` | Agent run completed successfully |
| `RUN_ERROR` | Agent run encountered an error |
| `STEP_STARTED` | New step/agent started execution |
| `STEP_FINISHED` | Step/agent completed execution |

### Text Message Events
| Event | Description |
|-------|-------------|
| `TEXT_MESSAGE_START` | Beginning of a text message |
| `TEXT_MESSAGE_CONTENT` | Chunk of message content (delta) |
| `TEXT_MESSAGE_END` | End of text message |
| `TEXT_MESSAGE_CHUNK` | Convenience: auto-manages start/end |

### State Events
| Event | Description |
|-------|-------------|
| `STATE_SNAPSHOT` | Complete state object |
| `STATE_DELTA` | Incremental state update (JSON Patch) |

### Custom Events
| Event | Description |
|-------|-------------|
| `CUSTOM` | Application-specific events (thinking, artifacts) |

---

## SSE Event Format

Events are streamed as Server-Sent Events:

```
event: RUN_STARTED
data: {"type":"RUN_STARTED","threadId":"...","runId":"..."}

event: STEP_STARTED
data: {"type":"STEP_STARTED","stepName":"contract-guardian"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"...","delta":"Analyzing..."}

event: RUN_FINISHED
data: {"type":"RUN_FINISHED","threadId":"...","runId":"..."}
```

---

## State Schema

The `STATE_SNAPSHOT` event provides workflow visibility:

```json
{
  "status": "planning|executing|complete|error",
  "current_agent": "contract-guardian",
  "risk_level": "none|low|medium|high|critical",
  "plan": {...}
}
```

---

## Frontend Integration

### CopilotKit (Recommended)
```tsx
import { CopilotKit } from "@copilotkit/react-core";

<CopilotKit runtimeUrl="http://localhost:8000/api/agui">
  <YourApp />
</CopilotKit>
```

### Custom AG-UI Client
```typescript
import { HttpAgent } from "@ag-ui/client";

const agent = new HttpAgent({ url: "http://localhost:8000/api/agui" });
agent.runAgent({ messages: [...] }).subscribe(event => {
  console.log(event.type, event);
});
```

---

## Available Agents

| ID | Purpose |
|----|---------|
| `Flagpilot-orchestrator` | Main orchestrator |
| `contract-guardian` | Contract analysis |
| `job-authenticator` | Job post verification |
| `payment-enforcer` | Payment protection |
| `scope-sentinel` | Scope creep detection |
| `risk-advisor` | Risk assessment |
| `dispute-mediator` | Dispute handling |
| `negotiation-assistant` | Negotiation help |
| `communication-coach` | Communication tips |
| `talent-vet` | Client/freelancer vetting |
| `profile-analyzer` | Profile optimization |
| `ghosting-shield` | Ghost client protection |
| `feedback-loop` | Feedback management |
| `application-filter` | Job filtering |
| `planner-role` | Task planning |
