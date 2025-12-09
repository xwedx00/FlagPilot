"""
FlagPilot API Routers

Core endpoints:
- health: Health checks
- stream: Main SSE chat endpoint
- files: File upload (MinIO → RAGFlow)
- missions: Chat persistence
- feedback: RLHF for Global Wisdom
"""

from . import health, stream, files, missions, feedback
