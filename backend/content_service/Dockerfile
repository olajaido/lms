FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/shared

# Install system dependencies including ffmpeg for video processing
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules first (from the shared directory)
COPY shared ./shared

# Copy content service code
COPY content_service .

# Debug: Check if shared modules were copied correctly
RUN ls -la /app/shared || echo "Shared directory not found"
RUN ls -la /app/shared/http_client.py || echo "http_client.py not found in shared directory"

# Create uploads directory
RUN mkdir -p uploads && chmod 755 uploads

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]