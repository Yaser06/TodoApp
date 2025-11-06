# Task Board - Minimal Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/

# Health check
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-9090}/health').read()"

# Expose default port (will auto-find if busy)
EXPOSE 9090

# Start with port auto-detection
CMD ["python", "-u", "backend/app.py"]
