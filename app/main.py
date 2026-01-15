# Import FastAPI and Pydantic modules
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
import uvicorn
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from .schema import HeadlineRequest, SentimentResponse, HeadlineCreate, HeadlinesResponse, HeadlineOut
from .db import get_db, Base, engine
from .db_models import Headline
from .scraper_service import ScraperService
from .models import analyze_headline_sentiment, get_analyzer

# Load environment variables from .env file
load_dotenv()

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Initialize FastAPI app instance
app = FastAPI(
    title="Financial News Sentiment Analyzer",
    description="Analyze sentiment of financial news headlines",
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI
    redoc_url=None  # Disable ReDoc
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        get_analyzer()  # Preload the model
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
        sentiment, commentary = analyze_headline_sentiment(request.headline)
        
        return SentimentResponse(
            sentiment=sentiment,
            commentary=commentary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") from e

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Mount static files for the frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Serve the frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_path = FRONTEND_DIR / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"message": "Financial News Sentiment Analyzer is running!", "status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=HOST, 
        port=PORT, 
        reload=DEBUG,
        log_level=log_level.lower()
    )

# Headlines storage and retrieval APIs

@app.post("/headlines", response_model=HeadlineOut)
def create_headline(headline: HeadlineCreate, db: Session = Depends(get_db)):
    try:
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
        try:
            dt = datetime.fromisoformat(start_date)
            stmt = stmt.where(Headline.published_at >= dt)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid start_date") from e
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            stmt = stmt.where(Headline.published_at <= dt)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid end_date") from e
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


@app.delete("/headlines/{headline_id}")
def delete_headline(headline_id: int, db: Session = Depends(get_db)):
    """Delete a specific headline by ID."""
    obj = db.get(Headline, headline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Headline not found")
    
    db.delete(obj)
    db.commit()
    
    return {"message": f"Headline {headline_id} deleted successfully"}


@app.delete("/headlines")
def clear_all_headlines(db: Session = Depends(get_db)):
    """Delete all headlines from the database."""
    try:
        # Count headlines before deletion
        count_stmt = select(func.count(Headline.id))
        total_count = db.execute(count_stmt).scalar()
        
        # Delete all headlines
        delete_stmt = select(Headline)
        headlines = db.execute(delete_stmt).scalars().all()
        
        for headline in headlines:
            db.delete(headline)
        
        db.commit()
        
        return {
            "message": "All headlines cleared successfully",
            "deleted_count": total_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing headlines: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear headlines: {str(e)}") from e


# Scraping endpoints

@app.post("/scrape")
async def scrape_headlines(
    source: str = "CNBC",
    max_headlines: int = 20,
    db: Session = Depends(get_db)
):
    """
    Manually trigger scraping of headlines from specified source.
    
    Args:
        source: Source to scrape from (CNBC, Yahoo Finance, Reuters, MarketWatch)
        max_headlines: Maximum number of headlines to scrape
        
    Returns:
        Scraping results with counts
    """
    try:
        scraper_service = ScraperService(db)
        results = await scraper_service.scrape_and_store_headlines(
            source=source,
            max_headlines=max_headlines
        )
        
        return {
            "message": f"Scraping completed for {source}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}") from e


@app.post("/scrape/all")
async def scrape_all_sources(
    max_headlines_per_source: int = 10,
    db: Session = Depends(get_db)
):
    """
    Scrape headlines from all available sources.
    
    Args:
        max_headlines_per_source: Maximum number of headlines per source
        
    Returns:
        Scraping results for all sources
    """
    try:
        scraper_service = ScraperService(db)
        results = await scraper_service.scrape_all_sources(
            max_headlines_per_source=max_headlines_per_source
        )
        
        total_scraped = sum(r['scraped'] for r in results.values())
        total_stored = sum(r['stored'] for r in results.values())
        
        return {
            "message": f"Scraping completed for all sources. Total: {total_scraped} scraped, {total_stored} stored",
            "results": results,
            "summary": {
                "total_scraped": total_scraped,
                "total_stored": total_stored,
                "sources": list(results.keys())
            }
        }
        
    except Exception as e:
        logger.error(f"Error in scrape all endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}") from e


@app.get("/scrape/stats")
def get_scraping_stats(db: Session = Depends(get_db)):
    """Get statistics about scraped headlines."""
    try:
        scraper_service = ScraperService(db)
        stats = scraper_service.get_scraping_stats()
        
        return {
            "message": "Scraping statistics",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting scraping stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") from e


@app.get("/scrape/recent")
def get_recent_scraped_headlines(
    source: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recently scraped headlines."""
    try:
        scraper_service = ScraperService(db)
        headlines = scraper_service.get_recent_headlines(source=source, limit=limit)
        
        return {
            "message": f"Recent headlines from {source or 'all sources'}",
            "headlines": headlines
        }
        
    except Exception as e:
        logger.error(f"Error getting recent headlines: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent headlines: {str(e)}") from e