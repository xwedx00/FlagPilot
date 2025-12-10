"""
FlagPilot Backend API
=====================
Multi-Agent SaaS Platform for Freelancers

Core Focus:
- MetaGPT-based AI agents (13 specialists)
- Team orchestration (MGX.dev style)
- RAGFlow integration for document understanding
- Chat/Mission persistence
"""

# =============================================================================
# CRITICAL: Set MetaGPT environment variables BEFORE any imports
# MetaGPT config2 validates on import, so env vars must be set first
# =============================================================================
import os

# =============================================================================
# Configuration
# =============================================================================
from config import settings

# Inject env vars for MetaGPT (must happen before imports)
settings.configure_metagpt_env()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
from loguru import logger
import os

# Configure logging
os.makedirs("logs", exist_ok=True)
logger.add("logs/flagpilot.log", rotation="500 MB", level=settings.LOG_LEVEL)

# Optimization: Suppress benign MetaGPT token warnings for custom models
def token_warning_filter(record):
    return "usage calculation failed" not in record["message"]

logger.add(lambda msg: None, filter=token_warning_filter)
# Note: loguru filters apply to handlers. The default handler needs to be filtered or we accept it.
# Actually, simpler to just log that we are suppressing it or leave it be if it's hard to filter default.
# Let's try to just use standard logging filter since MetaGPT might use standard logging.
import logging
class TokenWarningFilter(logging.Filter):
    def filter(self, record):
        return "usage calculation failed" not in record.getMessage()

logging.getLogger("metagpt").addFilter(TokenWarningFilter())



from lifecycle import lifespan


# (Logic moved to config.py)


app = FastAPI(
    title="FlagPilot Multi-Agent API",
    description="MetaGPT multi-agent platform for freelancers. 13 AI agents with team orchestration and RAGFlow.",
    version="3.0.0",
    lifespan=lifespan
)

# CORS (must be explicit for credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (simplified - core endpoints only)
from routers import health
from routers.stream import router as stream_router
from routers.files import router as files_router
from routers.missions import router as missions_router
from routers.feedback import router as feedback_router
from routers.history import router as history_router

from routers.credits import router as credits_router

app.include_router(health.router)
app.include_router(stream_router)    # Main SSE chat endpoint
app.include_router(files_router)      # File upload to MinIO/RAGFlow
app.include_router(missions_router)   # Chat persistence
app.include_router(feedback_router)   # RLHF feedback → Global Wisdom
app.include_router(history_router)    # Workflow History
app.include_router(credits_router)    # Billing / Usage




# Dynamic Agent Registry
from agents.registry import registry

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    agents: List[str]
    features: List[str]


@app.get("/")
async def root():
    """API root"""
    agents_list = registry.list_agents()
    return {
        "name": "FlagPilot Multi-Agent API",
        "version": "3.0.0",
        "description": "MetaGPT AI agents for freelancers",
        "agents": len(agents_list),
        "docs": "/docs",
        "features": [
            "MetaGPT Team Orchestration",
            "RAGFlow Document Understanding",
            "Personal Vault + Global Wisdom",
            f"{len(agents_list)} Specialist Agents"
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="3.0.0",
        agents=registry.list_agents(),
        features=[
            "MetaGPT Team Orchestration",
            "RAGFlow Integration",
            "PostgreSQL",
            "Redis Caching"
        ]
    )


@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents"""
    agents_list = registry.list_agents()
    return {
        "agents": agents_list,
        "count": len(agents_list)
    }


@app.get("/api/v1/team/capabilities")
async def team_capabilities():
    """Get team capabilities"""
    return {
        "capabilities": [
            "contract_review",
            "job_verification", 
            "payment_protection",
            "communication_coaching",
            "dispute_resolution"
        ],
        "supported_formats": ["pdf", "docx", "txt"],
        "rag_enabled": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
