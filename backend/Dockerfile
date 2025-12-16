# FlagPilot Backend
# =================
# Optimized with pip caching via BuildKit

FROM python:3.11-slim-bookworm as builder

WORKDIR /build

# System dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install dependencies with BuildKit cache mount
# This caches pip packages between builds - MUCH faster rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary -r requirements.txt

# =================
# Runtime Stage
# =================
FROM python:3.11-slim-bookworm

WORKDIR /app

# Runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GIT_PYTHON_REFRESH=quiet

# Create non-root user
RUN groupadd -r flagpilot && useradd -r -g flagpilot -d /app -s /sbin/nologin flagpilot \
    && chown -R flagpilot:flagpilot /app

USER flagpilot

EXPOSE 8000

# Health check with longer startup for MetaGPT init
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "run.py"]
