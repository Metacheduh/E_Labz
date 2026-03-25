# E-Labz Swarm Scheduler — Lean Cloud Run Image
# No browser/Playwright needed — posting goes through Typefully API
FROM python:3.13-slim

# Minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (copy first for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the scheduler needs
COPY orchestrator/ orchestrator/
COPY config/ config/

# Create runtime dirs
RUN mkdir -p output/research output/tweets data logs logs/syncs

# Set Python path so orchestrator package resolves
ENV PYTHONPATH=/app

# Cloud Run uses PORT env var; default 8080
ENV PORT=8080

# No health check needed — this is a background worker, not a web server
# Cloud Run with --no-cpu-throttling keeps it alive

# Run the scheduler loop
CMD ["python", "-m", "orchestrator.core.scheduler"]
