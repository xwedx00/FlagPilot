# FlagPilot Backend
# =================
# Minimal image: MetaGPT + FastAPI + RAGFlow

FROM python:3.11-slim-bookworm

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application code
COPY . .



# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GIT_PYTHON_REFRESH=quiet

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with bootstrap script (sets env vars before imports)
CMD ["python", "run.py"]
