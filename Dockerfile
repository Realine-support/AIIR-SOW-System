# Use Python 3.11 slim image (EXACT VERSION)
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY aiir-sow-system/requirements.txt /app/requirements.txt

# Install dependencies with Python 3.11
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY aiir-sow-system /app

# Expose port (Railway will provide PORT env var)
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
