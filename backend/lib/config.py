"""
Configuration Management
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings - Database-free backend"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Redis (for caching only)
    redis_url: str = "redis://localhost:6379"
    
    # RAGFlow
    ragflow_url: str = "http://ragflow:80"
    ragflow_api_key: Optional[str] = None
    
    # LLM - OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-4o-mini"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
