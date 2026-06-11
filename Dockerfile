FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY agents/ ./agents/
COPY data/ ./data/
COPY docs/ ./docs/

# Expose Foundry Hosted Agent port
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import httpx; httpx.get('http://localhost:8088/health')" || exit 1

# Start the agent server
CMD ["python", "main.py", "--serve"]
