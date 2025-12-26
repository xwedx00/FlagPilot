"""
FlagPilot Backend API
======================
LangGraph Multi-Agent Server with CopilotKit Integration

Architecture:
- FastAPI web framework
- LangGraph for multi-agent orchestration
- CopilotKit for frontend integration
- RAGFlow for knowledge retrieval
- Elasticsearch for memory persistence
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
logger.add("logs/Flagpilot.log", rotation="500 MB", level="INFO")

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
    description="LangGraph multi-agent server with CopilotKit integration. 14 AI agents with team orchestration and RAGFlow.",
    version="6.0.0",
)

# CORS - Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =============================================================================
# CopilotKit Integration (Primary)
# =============================================================================
try:
    from copilotkit.integrations.fastapi import add_fastapi_endpoint
    from lib.copilotkit import sdk

    # Add CopilotKit endpoint - this is the primary integration point for frontend
    add_fastapi_endpoint(app, sdk, "/copilotkit")
    logger.info("✅ CopilotKit endpoint registered at /copilotkit")
except ImportError as e:
    logger.warning(f"CopilotKit not available: {e}")

# =============================================================================
# DEBUG: Agent Inspection Endpoint
# =============================================================================
try:
    @app.get("/debug/agents")
    async def debug_agents():
        """Debug endpoint to list registered CopilotKit agents"""
        return {
            "agents": [a.name for a in sdk.agents],
            "sdk_type": str(type(sdk)),
            "agent_types": [str(type(a)) for a in sdk.agents]
        }
except Exception as e:
    logger.error(f"Failed to create debug endpoint: {e}")

# =============================================================================
# Routers
# =============================================================================
try:
    from routers import health
    app.include_router(health.router)  # /health endpoints
except ImportError:
    pass

try:
    from routers.agents import router as agents_router
    app.include_router(agents_router)  # /api/agents endpoints
except ImportError:
    pass

try:
    from routers import rag
    app.include_router(rag.router)  # /api/rag endpoints
except ImportError:
    pass

try:
    from routers import feedback
    app.include_router(feedback.router)  # /api/v1/feedback endpoints
except ImportError:
    pass


# =============================================================================
# Core Endpoints
# =============================================================================

# Agent list
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
        "version": "6.0.0",
        "description": "LangGraph multi-agent server with CopilotKit integration",
        "agents": len(AVAILABLE_AGENTS),
        "architecture": "LangGraph + CopilotKit",
        "docs": "/docs",
        "endpoints": {
            "copilotkit": "/copilotkit",
            "agents": "/api/agents",
            "rag": "/api/rag/search",
            "health": "/health",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="6.0.0",
        agents=AVAILABLE_AGENTS,
        features=[
            "LangGraph Team Orchestration",
            "RAGFlow Integration",
            "CopilotKit Protocol Streaming",
            "LangSmith Observability",
            "Elasticsearch Memory",
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
