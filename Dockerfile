# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install deps into a venv so the runtime stage stays clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Don't run as root (best practice for Azure Container Apps)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Azure Container Apps: expose port 8080 by default
EXPOSE 8080

# Start the FastAPI web API on port 8080 (Azure Container Apps default)
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
