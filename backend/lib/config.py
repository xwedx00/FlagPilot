"""
Configuration Management
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://flagpilot:flagpilot@localhost:5432/flagpilot"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    
    # LLM - OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    
    # LLM - OpenAI (alternative)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # RAG
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_collection_name: str = "flagpilot_global_rag"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
