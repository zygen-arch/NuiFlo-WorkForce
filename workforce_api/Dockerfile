# Use Python 3.11 as base image
FROM python:3.11-slim

# Install system dependencies including Ollama requirements
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 11434

# Create startup script that starts both Ollama and the API
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to be ready\n\
echo "⏳ Waiting for Ollama to start..."\n\
sleep 10\n\
\n\
# Pull Mistral model\n\
echo "📥 Downloading Mistral model..."\n\
ollama pull mistral:7b-instruct\n\
\n\
echo "🚀 Starting NuiFlo WorkForce API with Hybrid LLM..."\n\
# Start the FastAPI application\n\
exec uvicorn workforce_api.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ping && curl -f http://localhost:11434/api/version || exit 1

# Use startup script
CMD ["/app/start.sh"] 