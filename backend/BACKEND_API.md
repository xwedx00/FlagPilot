# FlagPilot Backend API Documentation

This document details the API endpoints and integration patterns for the FlagPilot backend, powered by MetaGPT and RAGFlow.

## Table of Contents
1. [Authentication](#authentication)
2. [Workflow Execution (RAG & Agents)](#workflow-execution-rag--agents)
3. [File Upload (RAG)](#file-upload-rag)
4. [History & Persistence](#history--persistence)
5. [System Health](#system-health)

---

## Base URL
`http://localhost:8000`

---

## Authentication

The backend uses JWT (JSON Web Tokens). Most endpoints require the `Authorization: Bearer <token>` header.

### 1. Login
**Endpoint**: `POST /auth/token`
**Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
| Field | Type | Description |
|-------|------|-------------|
| `username` | string | User's unique username |
| `password` | string | User's password |

**Response (200 OK)**:
```json
{
  "access_token": "ey...",
  "token_type": "bearer",
  "user": {
      "id": "user_id",
      "username": "user",
      "email": "user@test.com"
  }
}
```

### 2. Register
**Endpoint**: `POST /auth/register`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@test.com",
  "password": "securepassword",
  "full_name": "New User"
}
```

---

## Workflow Execution (RAG & Agents)

This is the core feature. Changes flow via **Server-Sent Events (SSE)**.

> ⚡ **Smart Orchestration**: The system automagically optimizes workflows. Simple queries (greetings, general questions) may return a single `message` event immediately, bypassing the full agent DAG.

### Endpoint: `POST /api/v1/stream/workflow`
**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "message": "User's problem statement...",
  "user_id": "current_user_id",
  "context": {
      "id": "current_user_id",
      "additional_field": "value"
  }
}
```

### SSE Event Stream Output
The stream returns events in two formats (Vercel AI SDK compatible & Standard JSON).

#### A. Standard Message
Event Type: `message`
```json
{
  "type": "message",
  "agent": "flagpilot",
  "content": "Text content to display to user"
}
```

#### B. Agent Status Update
Event Type: `agent_status`
Used to show "thinking" indicators or active agents in the UI.
```json
{
  "type": "agent_status",
  "agent": "contract-guardian",
  "status": "working" // or "completed", "error"
}
```

#### C. Workflow / Plan Update
Event Type: `workflow_update`
Contains the workflow plan for agent execution. Use this to render a visual progress chart.
```json
{
  "type": "workflow_update",
  "nodes": [
      {
          "id": "task-1",
          "agent": "contract-guardian",
          "status": "completed",
          "instruction": "Analyze contract..."
      },
      {
          "id": "risk-advisor-override-123",
          "agent": "risk-advisor",
          "status": "pending",
          "instruction": "CRITICAL OVERRIDE..."
      }
  ]
}
```

### 🚨 Handling "Fast-Fail" & Risk Advisor
If an agent detects a **CRITICAL RISK** (e.g., Scam, Unenforceable Contract), the backend will:
1.  Emit a `message` event containing `🚨 WORKFLOW INTERRUPTED 🚨`.
2.  Abort pending tasks.
3.  Inject a new task for the `risk-advisor` agent.
4.  The `risk-advisor` will output an emergency report.

**Frontend Action**:
-   If `risk-advisor` appears in `agent_status` or `workflow_update`, highlight it (e.g., Red Border).
-   Display the Interrupt Message prominently.

---

## File Upload (RAG)

Upload documents to the User's Knowledge Base.

### Endpoint: `POST /api/v1/files/upload`
**Headers**: `Authorization: Bearer <token>`

**Request (Multipart/Form-Data)**:
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | The document (PDF, TXT, MD) |

**Response**:
```json
{
  "filename": "contract.txt",
  "status": "uploaded",
  "size": 1024
}
```

---

## History & Persistence

Retrieve past workflow executions.

### 1. Get User History
**Endpoint**: `GET /api/v1/history/user/{user_id}`
**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
[
  {
      "id": "execution_uuid",
      "user_id": "user_id",
      "status": "completed", // or "failed", "running"
      "created_at": "timestamp",
      "completed_at": "timestamp",
      "plan_snapshot": {...}
  }
]
```

### 2. Get Single Execution Detail
**Endpoint**: `GET /api/v1/history/{execution_id}`
**Headers**: `Authorization: Bearer <token>`

**Response**:
Returns the full `WorkflowExecution` object with `results` (the final chat history/output).

---

## System Health

**Endpoint**: `GET /health`
Returns `{"status": "ok"}` if API and DB are reachable.
