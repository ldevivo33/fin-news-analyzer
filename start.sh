#!/bin/bash

# Financial News Sentiment Analyzer - Cloud Startup Script

set -e

echo "Starting Financial News Sentiment Analyzer..."

# Set default environment variables if not set
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}
export DEBUG=${DEBUG:-"false"}
export LOG_LEVEL=${LOG_LEVEL:-"info"}
export DB_TYPE=${DB_TYPE:-"sqlite"}
export DB_NAME=${DB_NAME:-"finnews"}

# Create necessary directories
mkdir -p backend
mkdir -p logs

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Run database migrations/initialization
echo "Initializing database..."
python -c "
from app.db import Base, engine
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Start the application
echo "Starting FastAPI application on $HOST:$PORT"
echo "Debug mode: $DEBUG"
echo "Log level: $LOG_LEVEL"

if [ "$DEBUG" = "true" ]; then
    uvicorn app.main:app --host $HOST --port $PORT --reload --log-level $LOG_LEVEL
else
    uvicorn app.main:app --host $HOST --port $PORT --log-level $LOG_LEVEL
fi
