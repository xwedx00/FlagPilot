#!/usr/bin/env python3
"""
FlagPilot Entry Point v7.0
===========================
LangGraph multi-agent server with LangSmith observability.
"""

import os
import sys

# =============================================================================
# CRITICAL: Set environment variables BEFORE importing anything else
# =============================================================================

try:
    from config import settings
except ImportError:
    # If run as script, add current dir to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import settings

# Configure LangSmith tracing (must be done before importing LangChain)
if settings.configure_langsmith():
    print(f"[Bootstrap] LangSmith tracing enabled for project: {settings.langsmith_project}")
else:
    print("[Bootstrap] LangSmith tracing disabled (no API key)")

# Log configuration
print(f"[Bootstrap] Model: {settings.openrouter_model}")
print(f"[Bootstrap] OpenRouter API Key set: {bool(settings.openrouter_api_key)}")
print(f"[Bootstrap] Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
print(f"[Bootstrap] Elasticsearch: {settings.es_url}")
print(f"[Bootstrap] MinIO: {settings.minio_endpoint}")

# =============================================================================
# Run uvicorn server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Enable reload for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        reload_dirs=["/app"]
    )
