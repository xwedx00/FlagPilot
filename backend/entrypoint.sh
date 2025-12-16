#!/bin/bash
# FlagPilot Backend Entrypoint
# Fixes metagpt schema permissions at runtime (needed for volume mounts)

# Create metagpt schemas directory if it doesn't exist
mkdir -p /app/metagpt/tools/schemas
chmod -R 777 /app/metagpt/tools/schemas 2>/dev/null || true

# Create .metagpt config directory
mkdir -p /app/.metagpt
chmod 777 /app/.metagpt 2>/dev/null || true

# Start the application
exec python run.py "$@"
