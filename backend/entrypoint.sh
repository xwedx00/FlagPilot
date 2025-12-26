#!/bin/bash
# FlagPilot Backend Entrypoint
# LangGraph-based multi-agent system

# Create logs directory if needed
mkdir -p /app/logs
chmod -R 777 /app/logs 2>/dev/null || true

# Start the application
exec python run.py "$@"
