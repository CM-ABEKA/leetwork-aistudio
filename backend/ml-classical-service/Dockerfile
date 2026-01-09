# Multi-stage Dockerfile for FastAPI classical ML service

# ============================================
# DEVELOPMENT STAGE
# ============================================
FROM python:3.11-slim AS development

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8010

# Development command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]

# ============================================
# PRODUCTION STAGE
# ============================================
FROM python:3.11-slim AS production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8010

# Production command (will be overridden by docker-compose)
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8010"]
