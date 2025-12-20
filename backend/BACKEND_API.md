# Backend API & AG-UI Protocol Specification

## Overview
FlagPilot's backend exposes a **Server-Sent Events (SSE)** API that adheres to the **AG-UI Protocol**. This allows the frontend (using CopilotKit) to receive real-time updates about agent orchestration, state changes, and streaming text responses.

## Base URL
`http://localhost:8000/api`

## Authentication
Currently, the AG-UI endpoints are open to the internal network (accessed via Next.js proxy). In production, `Authorization: Bearer <token>` is required.

---

## 1. Agent Discovery

### `GET /agui/info`
**Purpose**: Used by CopilotKit to discover available agents and their capabilities.
**Response Format**: JSON Object (Map)

```json
{
  "service": "FlagPilot AG-UI",
  "agents": {
    "flagpilot_orchestrator": {
      "id": "flagpilot_orchestrator",
      "name": "FlagPilotOrchestrator",
      "profile": "Workflow Manager",
      "goal": "Orchestrate the perfect team...",
      "constraints": "Optimize for efficiency..."
    },
    "contract-guardian": {
      "id": "contract-guardian",
      "name": "ContractGuardian",
      "description": "Analyzes legal contracts..."
    }
  }
}
```

---

## 2. Event Stream (Chat & Orchestration)

### `POST /agui`
**Purpose**: Primary interaction endpoint. Handles both orchestration (Team) and direct agent communication.
**Headers**:
- `Content-Type: application/json`
- `Accept: text/event-stream`

**Request Body**:
```json
{
  "thread_id": "uuid-string",
  "run_id": "uuid-string",
  "agent_id": "flagpilot_orchestrator", // Optional, defaults to team
  "messages": [
    {
      "role": "user",
      "content": "Analyze this contract for risks..."
    }
  ],
  "context": [],
  "state": {}
}
```

**SSE Event Stream**:
The server streams line-delimited JSON events. Each event is a JSON object encoded by the AG-UI `EventEncoder`.

#### Key Events
1.  **RunStarted**
    ```json
    {"type": "RUN_STARTED", "thread_id": "...", "run_id": "..."}
    ```

2.  **StateSnapshot** (Initial State)
    ```json
    {"type": "STATE_SNAPSHOT", "snapshot": {"status": "planning", "risk_level": "none"}}
    ```

3.  **StepStarted** (Orchestrator Planning)
    ```json
    {"type": "STEP_STARTED", "step_name": "orchestrator-planning"}
    ```

4.  **StateDelta** (Plan Update)
    ```json
    {"type": "STATE_DELTA", "delta": [{"op": "add", "path": "/plan", "value": {...}}]}
    ```

5.  **ActivitySnapshot** (Agent Execution Progress)
    ```json
    {
      "type": "ACTIVITY_SNAPSHOT",
      "activity_type": "AGENT_EXECUTION",
      "content": {
        "agent_id": "contract-guardian",
        "status": "running",
        "progress": 33
      }
    }
    ```

6.  **TextMessageContent** (Streaming Response)
    ```json
    {"type": "TEXT_MESSAGE_CONTENT", "message_id": "...", "delta": "Analysis complete..."}
    ```

7.  **RunFinished**
    ```json
    {"type": "RUN_FINISHED", "result": {"status": "COMPLETED"}}
    ```

---

## 3. RAG & Memory Integration (Internal)

The backend automatically injects context into the `POST /agui` flow:

1.  **User Profile**: Fetched from ElasticSearch (`Flagpilot_user_profiles`).
2.  **Global Wisdom**: Fetched from Experience Gallery (`Flagpilot_experience_gallery`).
3.  **RAG Context**: Fetched from RAGFlow specific to the user's query.

This is transparent to the API client but affects the agent's behavior.
