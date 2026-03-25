# Use Python 3.11 slim image (EXACT VERSION)
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy application code FIRST (to bust Docker cache)
COPY aiir-sow-system /app

# Verify Python version
RUN python --version

# Install dependencies with Python 3.11 (NO CACHE, FRESH INSTALL)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Expose port (Railway will provide PORT env var)
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
