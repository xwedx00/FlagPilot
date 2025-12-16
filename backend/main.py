"""
FlagPilot Backend API - Simplified
==================================
Pure MetaGPT Agent Server

Core Focus:
- MetaGPT-based AI agents (17 specialists)
- Team orchestration (MGX.dev style)
- RAGFlow integration for document understanding

NOTE: Auth, chat persistence, and UI are handled by the frontend (Vercel AI Chatbot).
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

# Apply Billing Patches
from lib.patches import apply_metagpt_patches
apply_metagpt_patches()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
from loguru import logger
import logging

# Configure logging
os.makedirs("logs", exist_ok=True)
logger.add("logs/flagpilot.log", rotation="500 MB", level=settings.LOG_LEVEL)

# Suppress benign MetaGPT token warnings for custom models
class TokenWarningFilter(logging.Filter):
    def filter(self, record):
        return "usage calculation failed" not in record.getMessage()

logging.getLogger("metagpt").addFilter(TokenWarningFilter())


# =============================================================================
# App Setup
# =============================================================================
app = FastAPI(
    title="FlagPilot Agent API",
    description="Pure MetaGPT multi-agent server. 17 AI agents with team orchestration and RAGFlow.",
    version="4.0.0",
)

# CORS - Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =============================================================================
# Routers (Simplified)
# =============================================================================
from routers import health
from routers.agents import router as agents_router
from routers import rag

app.include_router(health.router)      # /health endpoints
app.include_router(agents_router)      # /api/agents + /api/team endpoints
app.include_router(rag.router)         # /api/rag endpoints


# =============================================================================
# Core Endpoints
# =============================================================================
from agents.registry import registry


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    agents: List[str]
    features: List[str]


@app.get("/")
async def root():
    """API root - service information"""
    agents_list = registry.list_agents()
    return {
        "name": "FlagPilot Agent API",
        "version": "4.0.0",
        "description": "Pure MetaGPT agent server for freelancers",
        "agents": len(agents_list),
        "docs": "/docs",
        "endpoints": {
            "agents": "/api/agents",
            "team": "/api/team/chat",
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
        version="4.0.0",
        agents=registry.list_agents(),
        features=[
            "MetaGPT Team Orchestration",
            "RAGFlow Integration",
            "SSE Streaming",
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
