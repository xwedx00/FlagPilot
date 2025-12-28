"""
FlagPilot Backend API v7.0
==========================
LangGraph Multi-Agent Server with CopilotKit Integration

Architecture:
- FastAPI web framework
- LangGraph for multi-agent orchestration
- CopilotKit for frontend integration
- Qdrant for vector RAG
- MinIO for file storage
- Elasticsearch for memory/wisdom
- PostgreSQL for LangGraph checkpoints
- LangSmith for observability

NOTE: Auth and chat persistence are handled by the frontend.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
from loguru import logger

# =============================================================================
# Configuration
# =============================================================================

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Configure logging
logger.add("logs/flagpilot.log", rotation="500 MB", level="INFO")

# Configure LangSmith (if API key is set)
from config import settings
if settings.configure_langsmith():
    logger.info("✅ LangSmith tracing enabled")
else:
    logger.info("ℹ️ LangSmith tracing disabled (no API key)")


# =============================================================================
# App Setup
# =============================================================================
app = FastAPI(
    title="FlagPilot Agent API",
    description="LangGraph multi-agent server with CopilotKit + Qdrant + MinIO. 17 AI agents with team orchestration.",
    version="7.0.0",
)

# CORS - Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =============================================================================
# CopilotKit Integration (AG-UI Protocol)
# =============================================================================
try:
    from ag_ui_langgraph import add_langgraph_fastapi_endpoint
    from lib.copilotkit.sdk import flagpilot_agent

    add_langgraph_fastapi_endpoint(
        app=app,
        agent=flagpilot_agent,
        path="/copilotkit",
    )
    logger.info("✅ CopilotKit AG-UI endpoint registered at /copilotkit")
except ImportError as e:
    logger.warning(f"CopilotKit AG-UI not available: {e}")
except Exception as e:
    logger.error(f"CopilotKit AG-UI setup error: {e}")

# =============================================================================
# DEBUG: Agent Inspection Endpoint
# =============================================================================
@app.get("/debug/agents")
async def debug_agents():
    """Debug endpoint to list registered CopilotKit agents"""
    try:
        from lib.copilotkit.sdk import flagpilot_agent
        return {
            "agents": [flagpilot_agent.name],
            "agent_type": str(type(flagpilot_agent)),
            "description": flagpilot_agent.description[:100] + "..."
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# Routers
# =============================================================================
try:
    from routers import health
    app.include_router(health.router)
except ImportError:
    pass

try:
    from routers.agents import router as agents_router
    app.include_router(agents_router)
except ImportError:
    pass

try:
    from routers import rag
    app.include_router(rag.router)
except ImportError:
    pass

try:
    from routers import feedback
    app.include_router(feedback.router)
except ImportError:
    pass

try:
    from routers import memory
    app.include_router(memory.router)
except ImportError:
    pass


# =============================================================================
# Core Endpoints
# =============================================================================

AVAILABLE_AGENTS = [
    "contract-guardian",
    "job-authenticator",
    "scope-sentinel",
    "payment-enforcer",
    "dispute-mediator",
    "communication-coach",
    "negotiation-assistant",
    "profile-analyzer",
    "ghosting-shield",
    "risk-advisor",
    "talent-vet",
    "application-filter",
    "feedback-loop",
    "planner-role",
]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    agents: List[str]
    features: List[str]


@app.get("/")
async def root():
    """API root - service information"""
    return {
        "name": "FlagPilot Agent API",
        "version": "7.0.0",
        "description": "LangGraph multi-agent server with CopilotKit + Qdrant + MinIO",
        "agents": len(AVAILABLE_AGENTS),
        "architecture": "LangGraph + CopilotKit + Qdrant + PostgreSQL",
        "docs": "/docs",
        "endpoints": {
            "copilotkit": "/copilotkit",
            "agents": "/api/agents",
            "rag": "/api/v1/rag",
            "health": "/health",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="7.0.0",
        agents=AVAILABLE_AGENTS,
        features=[
            "LangGraph Team Orchestration",
            "Qdrant Vector RAG",
            "MinIO File Storage",
            "CopilotKit Protocol Streaming",
            "LangSmith Observability",
            "Elasticsearch Memory",
            "PostgreSQL Checkpoints",
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
