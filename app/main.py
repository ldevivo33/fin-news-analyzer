# Import FastAPI and Pydantic modules 
from fastapi import FastAPI, HTTPException, Depends, Query
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
    # Ensure DB tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")

#Import Pydantic models from schema.py
from .schema import HeadlineRequest, SentimentResponse, HeadlineCreate, HeadlinesResponse, HeadlineOut
from .db import get_db, Base, engine
from .db_models import Headline
from sqlalchemy.orm import Session
from sqlalchemy import select, func

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


# Headlines storage and retrieval APIs

@app.post("/headlines", response_model=HeadlineOut)
def create_headline(headline: HeadlineCreate, db: Session = Depends(get_db)):
    try:
        from .models import analyze_headline_sentiment
        sentiment, commentary = analyze_headline_sentiment(headline.title)
    except Exception as e:
        sentiment, commentary = None, f"Analysis failed: {e}"

    db_obj = Headline(
        source=headline.source,
        title=headline.title,
        url=headline.url,
        published_at=headline.published_at,
        raw_text=headline.raw_text,
        sentiment=sentiment,
        commentary=commentary,
        model_confidence=None,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@app.get("/headlines", response_model=HeadlinesResponse)
def list_headlines(
    db: Session = Depends(get_db),
    source: str | None = Query(None),
    sentiment: str | None = Query(None, pattern="^(positive|neutral|negative)$"),
    start_date: str | None = Query(None, description="ISO8601 start datetime"),
    end_date: str | None = Query(None, description="ISO8601 end datetime"),
    q: str | None = Query(None, description="Search in title"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    stmt = select(Headline)

    if source:
        stmt = stmt.where(Headline.source == source)
    if sentiment:
        stmt = stmt.where(Headline.sentiment == sentiment)
    if start_date:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(start_date)
            stmt = stmt.where(Headline.published_at >= dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid start_date")
    if end_date:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(end_date)
            stmt = stmt.where(Headline.published_at <= dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid end_date")
    if q:
        stmt = stmt.where(Headline.title.ilike(f"%{q}%"))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    stmt = stmt.order_by(Headline.published_at.desc().nullslast(), Headline.created_at.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    return {"items": rows, "total": total}


@app.get("/headlines/{headline_id}", response_model=HeadlineOut)
def get_headline(headline_id: int, db: Session = Depends(get_db)):
    obj = db.get(Headline, headline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Headline not found")
    return obj