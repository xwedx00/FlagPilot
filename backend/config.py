
from pydantic_settings import BaseSettings
from typing import Optional

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
    
    # Redis (no PostgreSQL - database-free backend)
    REDIS_URL: str = "redis://localhost:6379"
    
    # RAGFlow
    RAGFLOW_URL: str = "http://ragflow:80"
    RAGFLOW_API_KEY: Optional[str] = None
    
    # MetaGPT Legacy Config (Derived)
    # These are needed for MetaGPT's internal config
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_API_MODEL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" # Allow extra vars from docker env

    def configure_metagpt_env(self):
        """
        Injects settings into os.environ for MetaGPT to consume.
        MetaGPT config reads directly from os.environ on import.
        """
        import os
        os.environ["OPENAI_API_KEY"] = self.OPENROUTER_API_KEY
        os.environ["OPENAI_API_BASE"] = self.OPENROUTER_BASE_URL
        os.environ["OPENAI_API_MODEL"] = self.OPENROUTER_MODEL
        
        # MetaGPT specific
        os.environ["METAGPT_LLM_API_TYPE"] = "openai"
        os.environ["METAGPT_LLM_API_KEY"] = self.OPENROUTER_API_KEY
        os.environ["METAGPT_LLM_BASE_URL"] = self.OPENROUTER_BASE_URL
        os.environ["METAGPT_LLM_MODEL"] = self.OPENROUTER_MODEL

# Singleton instance
settings = Settings()


def get_configured_llm():
    """
    Returns a configured LLM instance for actions to use.
    Relies on MetaGPT's default config loading (which we patched in run.py).
    """
    from metagpt.llm import LLM
    try:
        return LLM()
    except Exception as e:
        # Fallback if specific config missing, though likely handled by LLM()
        print(f"Error creating LLM: {e}")
        raise
