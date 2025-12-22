# FlagPilot Backend - Multi-Venv Isolation Architecture
# ======================================================
# 4 completely isolated virtual environments:
# - Core: FastAPI web server (main Python)
# - CopilotKit: AI integration SDK
# - MetaGPT: Multi-agent framework
# - RAGFlow: Knowledge retrieval SDK
#
# Each venv has its complete dependency tree - zero conflicts possible.

FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# System dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files
COPY requirements-core.txt \
    requirements-copilotkit.txt \
    requirements-metagpt.txt \
    requirements-ragflow.txt \
    ./

# ============================================
# VENV 1: Core (installed in main Python)
# ============================================
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary -r requirements-core.txt

# ============================================
# VENV 2: CopilotKit (isolated)
# ============================================
RUN python -m venv /venv-copilotkit
RUN --mount=type=cache,target=/root/.cache/pip \
    /venv-copilotkit/bin/pip install --prefer-binary -r requirements-copilotkit.txt

# ============================================
# VENV 3: MetaGPT (isolated)
# ============================================
RUN python -m venv /venv-metagpt
RUN --mount=type=cache,target=/root/.cache/pip \
    /venv-metagpt/bin/pip install --prefer-binary -r requirements-metagpt.txt

# ============================================
# VENV 4: RAGFlow (isolated)
# ============================================
RUN python -m venv /venv-ragflow
RUN --mount=type=cache,target=/root/.cache/pip \
    /venv-ragflow/bin/pip install --prefer-binary -r requirements-ragflow.txt

# ============================================
# Runtime Stage
# ============================================
FROM python:3.11-slim-bookworm

WORKDIR /app

# Runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (core env)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code FIRST
COPY . .

# Copy isolated virtual environments AFTER app code (prevents overwrite)
COPY --from=builder /venv-copilotkit /app/venv-copilotkit
COPY --from=builder /venv-metagpt /app/venv-metagpt
COPY --from=builder /venv-ragflow /app/venv-ragflow

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GIT_PYTHON_REFRESH=quiet

# Venv paths for runners
ENV COPILOTKIT_VENV=/app/venv-copilotkit
ENV METAGPT_VENV=/app/venv-metagpt
ENV RAGFLOW_VENV=/app/venv-ragflow

# Create directories and set permissions
RUN mkdir -p /app/logs /app/.metagpt /app/metagpt/tools/schemas \
    && chmod -R 777 /app/logs \
    && chmod -R 777 /app/venv-metagpt/lib/python3.11/site-packages/metagpt 2>/dev/null || true

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "run.py"]
