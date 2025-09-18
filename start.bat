@echo off
REM Financial News Sentiment Analyzer - Windows Cloud Startup Script

echo Starting Financial News Sentiment Analyzer...

REM Set default environment variables if not set
if not defined HOST set HOST=0.0.0.0
if not defined PORT set PORT=8000
if not defined DEBUG set DEBUG=false
if not defined LOG_LEVEL set LOG_LEVEL=INFO
if not defined DB_TYPE set DB_TYPE=sqlite
if not defined DB_NAME set DB_NAME=finnews

REM Create necessary directories
if not exist backend mkdir backend
if not exist logs mkdir logs

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Run database migrations/initialization
echo Initializing database...
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"

REM Start the application
echo Starting FastAPI application on %HOST%:%PORT%
echo Debug mode: %DEBUG%
echo Log level: %LOG_LEVEL%

if "%DEBUG%"=="true" (
    uvicorn app.main:app --host %HOST% --port %PORT% --reload --log-level %LOG_LEVEL%
) else (
    uvicorn app.main:app --host %HOST% --port %PORT% --log-level %LOG_LEVEL%
)
