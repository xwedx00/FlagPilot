"""
FlagPilot Backend Configuration v7.0
=====================================
Settings for LangGraph + Qdrant + Elasticsearch + MinIO + PostgreSQL
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ===========================================
    # Core Settings
    # ===========================================
    app_name: str = "FlagPilot Agent API"
    app_version: str = "7.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # ===========================================
    # OpenRouter LLM
    # ===========================================
    openrouter_api_key: str = ""
    openrouter_model: str = "kwaipilot/kat-coder-pro:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # ===========================================
    # Embedding Model (via OpenRouter or OpenAI)
    # ===========================================
    embedding_model: str = "text-embedding-3-small"

    # ===========================================
    # PostgreSQL (LangGraph Checkpoints + Auth)
    # ===========================================
    database_url: Optional[str] = None

    # ===========================================
    # Elasticsearch (Wisdom, Profiles, Chat Logs)
    # ===========================================
    es_host: str = "es01"
    es_port: int = 9200

    @property
    def es_url(self) -> str:
        return f"http://{self.es_host}:{self.es_port}"

    # ===========================================
    # Qdrant (Vector Database for RAG)
    # ===========================================
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "flagpilot_documents"

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    # ===========================================
    # MinIO (S3-Compatible File Storage)
    # ===========================================
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "flagpilot-files"
    minio_secure: bool = False

    # ===========================================
    # Redis (Caching + Rate Limiting)
    # ===========================================
    redis_url: str = "redis://localhost:6379"

    # ===========================================
    # LangSmith (Observability)
    # ===========================================
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "flagpilot"

    def configure_langsmith(self) -> bool:
        """Configure LangSmith tracing if API key is available"""
        if self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project
            return True
        return False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
