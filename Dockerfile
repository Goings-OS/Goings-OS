FROM python:3.11-slim

# Prevent bytecode compilation and unbuffer output streams
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create unprivileged non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8080

# Production Gunicorn worker management
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "app:app"]
