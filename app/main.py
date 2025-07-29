# Import FastAPI and Pydantic modules 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Initialize FastAPI app instance
app = FastAPI(
    title="Financial News Sentiment Analyzer",
    description="Analyze sentiment of financial news headlines",
    version="1.0.0"
)

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

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Financial News Sentiment Analyzer is running!"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)