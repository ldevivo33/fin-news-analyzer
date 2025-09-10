# Import FastAPI and Pydantic modules 
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app instance
app = FastAPI(
    title="Financial News Sentiment Analyzer",
    description="Analyze sentiment of financial news headlines",
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI
    redoc_url=None  # Disable ReDoc
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload the model at startup
@app.on_event("startup")
async def startup_event():
    """Preload the sentiment analysis model at startup."""
    logger.info("Starting up Financial News Sentiment Analyzer...")
    try:
        from .models import get_analyzer
        analyzer = get_analyzer()
        logger.info("Model preloaded successfully!")
    except Exception as e:
        logger.error(f"Failed to preload model: {e}")
        logger.info("App will use fallback analysis if needed.")

#Import Pydantic models from schema.py
from .schema import HeadlineRequest, SentimentResponse

# Define POST /analyze endpoint:
#   - Accepts request with headline
#   - Calls sentiment prediction function (stub for now)
#   - Generates simple commentary (stub for now)
#   - Returns response with sentiment and commentary
@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: HeadlineRequest):
    """
    Analyze the sentiment of a financial news headline.
    
    Args:
        request: HeadlineRequest containing the headline to analyze
        
    Returns:
        SentimentResponse with sentiment analysis results
    """
    try:
        # For now, let's create a simple rule-based sentiment analyzer
        sentiment, commentary = analyze_headline_sentiment(request.headline)
        
        return SentimentResponse(
            sentiment=sentiment,
            commentary=commentary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Import sentiment analysis function from models.py
from .models import analyze_headline_sentiment

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the React frontend
@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    return FileResponse("frontend/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"message": "Financial News Sentiment Analyzer is running!", "status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)