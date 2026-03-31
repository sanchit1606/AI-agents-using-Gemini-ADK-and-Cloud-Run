# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py agent.py schemas.py index.html ./

# Expose port
EXPOSE 8000

# Set environment variable for Cloud Run
ENV PORT=8000

# Run the application
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT
