"""
FlagPilot Configuration
=======================
Centralized configuration with Pydantic validation.
Includes LangSmith observability settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Centralized configuration with Pydantic validation.
    Reads from environment variables and .env file.
    """
    # App
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev-secret-key-change-in-prod"

    # LLM (OpenRouter)
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # LangSmith Observability
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "flagpilot"
    LANGSMITH_TRACING: bool = True
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # RAGFlow
    RAGFLOW_URL: str = "http://ragflow:80"
    RAGFLOW_API_KEY: Optional[str] = None
    RAGFLOW_EMBEDDING_MODEL: str = "text-embedding-3-small@OpenAI"
    
    # ElasticSearch (Memory System)
    ES_HOST: str = "es01"
    ES_PORT: int = 9200
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra vars from docker env

    def configure_langsmith(self):
        """
        Configure LangSmith tracing via environment variables.
        Call this at application startup.
        """
        if self.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true" if self.LANGSMITH_TRACING else "false"
            os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
            return True
        return False


# Singleton instance
settings = Settings()


def get_llm(**kwargs):
    """
    Returns a configured ChatOpenAI instance for LangChain.
    
    Args:
        **kwargs: Override default LLM settings
        
    Returns:
        ChatOpenAI instance configured for OpenRouter
    """
    from langchain_openai import ChatOpenAI
    
    return ChatOpenAI(
        model=kwargs.get("model", settings.OPENROUTER_MODEL),
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=kwargs.get("temperature", 0.3),
        max_tokens=kwargs.get("max_tokens", 2000)
    )


# Legacy alias for backward compatibility during migration
def get_configured_llm():
    """Legacy function - use get_llm() instead"""
    return get_llm()
