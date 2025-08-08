# Data Validation Tool Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash datavalidation && \
    chown -R datavalidation:datavalidation /app
USER datavalidation

# Expose port (if needed for web interface in future)
EXPOSE 8000

# Set default command
CMD ["python", "run_validation.py", "--help"] 