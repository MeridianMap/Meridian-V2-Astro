# syntax=docker/dockerfile:1

# --- Frontend build stage ---
FROM node:18-slim AS frontend-build

WORKDIR /app

# Copy frontend package.json and install dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci

# Copy frontend source code
COPY frontend ./frontend

# Set build-time environment variables for Vite
ARG VITE_GEOAPIFY_API_KEY
ARG VITE_ACCESS_PASSWORD
ARG VITE_REQUIRE_AUTH
ENV VITE_GEOAPIFY_API_KEY=${VITE_GEOAPIFY_API_KEY}
ENV VITE_ACCESS_PASSWORD=${VITE_ACCESS_PASSWORD}
ENV VITE_REQUIRE_AUTH=${VITE_REQUIRE_AUTH}

# Build the frontend with environment variables available
RUN cd frontend && npm run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-build

# Install system dependencies for Swiss Ephemeris and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt backend/requirements.lock ./backend/
RUN pip install --upgrade pip && \
    pip install -r backend/requirements.txt

# Copy backend source code
COPY backend ./backend

# Copy ephemeris data if it exists
COPY backend/ephe ./backend/ephe

# --- Final production stage ---
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from backend build stage
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /usr/local/bin /usr/local/bin

# Copy backend application
COPY --from=backend-build /app/backend ./backend

# Copy built frontend from frontend build stage
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Set environment variables
ENV FLASK_APP=backend/api.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# Start the Flask application
CMD ["sh", "-c", "cd backend && gunicorn api:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 60"]
