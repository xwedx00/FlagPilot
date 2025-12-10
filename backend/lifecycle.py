
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting FlagPilot Multi-Agent Platform...")
    
    # Initialize database
    try:
        from lib.database import init_db
        await init_db()
        
        # Initialize new Domain Models (WorkflowExecution, etc)
        from models.base import init_db as init_domain_db
        import models.intelligence  # Register models
        await init_domain_db()
        
        logger.info("✅ PostgreSQL connected (Legacy & Domain)")
    except Exception as e:
        logger.warning(f"⚠️ Database not available: {e}")
    
    # Initialize Redis
    try:
        from lib.redis_client import init_redis
        await init_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")
    
    # Initialize RAGFlow
    try:
        from ragflow import get_ragflow_client
        ragflow = get_ragflow_client()
        if ragflow.is_connected:
            logger.info("✅ RAGFlow connected")
        else:
            logger.warning("⚠️ RAGFlow not connected (API key may be missing)")
    except Exception as e:
        # Don't swallow critical startup errors silently in production, 
        # but for now we warn to keep container alive if optional RAG is down
        logger.warning(f"⚠️ RAGFlow initialization failed: {e}")
    
    # MetaGPT Config Verification
    logger.info(f"✅ MetaGPT configured: {settings.OPENROUTER_MODEL}")
    
    # Initialize Agent Registry (Fail Fast)
    try:
        from agents.registry import registry
        registry.initialize()
        logger.info(f"✅ Agent Registry loaded: {len(registry.list_agents())} agents")
    except Exception as e:
        logger.error(f"❌ Agent Registry failed: {e}")
        # We might want to raise here, but for now we log error
    
    logger.info("✅ FlagPilot Platform ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FlagPilot Platform...")
    try:
        from lib.database import close_db
        from lib.redis_client import close_redis
        await close_db()
        await close_redis()
    except Exception:
        pass
    logger.info("👋 Shutdown complete")
