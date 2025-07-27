FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application code
COPY workforce_api/ ./workforce_api/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ping || exit 1

# Start command
CMD ["uvicorn", "workforce_api.main:app", "--host", "0.0.0.0", "--port", "8000"] 