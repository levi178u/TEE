# FROM python:3.11

# WORKDIR /app

# COPY server/ /app/server
# COPY .env /app/.env

# RUN pip install --no-cache-dir -r /app/server/requirements.txt

# EXPOSE 8000

# CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]

# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for psycopg2 and building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]