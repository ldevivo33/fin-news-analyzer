from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import logging

from .scraper import (
    scrape_cnbc_headlines, 
    scrape_yahoo_finance_headlines, 
    scrape_reuters_headlines, 
    scrape_marketwatch_headlines
)
from .db_models import Headline
from .models import analyze_headline_sentiment

logger = logging.getLogger(__name__)

class ScraperService:
    """Service for scraping and storing headlines with sentiment analysis."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def scrape_and_store_headlines(
        self, 
        source: str = "CNBC", 
        max_headlines: int = 20,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Scrape headlines and store them in the database with sentiment analysis.
        
        Args:
            source: Source name for headlines
            max_headlines: Maximum number of headlines to scrape
            skip_existing: Skip headlines that already exist (by URL)
            
        Returns:
            Dictionary with counts of scraped, stored, and skipped headlines
        """
        results = {
            'scraped': 0,
            'stored': 0,
            'skipped': 0,
            'errors': 0
        }
        
        try:
            # Scrape headlines based on source
            source_upper = source.upper()
            if source_upper == "CNBC":
                headlines_data = await scrape_cnbc_headlines(max_headlines)
            elif source_upper in ["YAHOO", "YAHOO FINANCE"]:
                headlines_data = await scrape_yahoo_finance_headlines(max_headlines)
            elif source_upper == "REUTERS":
                headlines_data = await scrape_reuters_headlines(max_headlines)
            elif source_upper == "MARKETWATCH":
                headlines_data = await scrape_marketwatch_headlines(max_headlines)
            else:
                logger.warning(f"Unknown source: {source}")
                return results
            
            results['scraped'] = len(headlines_data)
            logger.info(f"Scraped {len(headlines_data)} headlines from {source}")
            
            # Process each headline
            for headline_data in headlines_data:
                try:
                    # Check if headline already exists (if skip_existing is True)
                    if skip_existing:
                        existing = self.db.execute(
                            select(Headline).where(Headline.url == headline_data['url'])
                        ).scalar_one_or_none()
                        
                        if existing:
                            results['skipped'] += 1
                            continue
                    
                    # Analyze sentiment
                    sentiment, commentary = self._analyze_sentiment(headline_data['title'])
                    
                    # Create headline record
                    headline = Headline(
                        source=headline_data['source'],
                        title=headline_data['title'],
                        url=headline_data['url'],
                        published_at=datetime.fromisoformat(headline_data['published_at']) if headline_data.get('published_at') else None,
                        raw_text=None,  # We're only scraping headlines, not full articles
                        sentiment=sentiment,
                        commentary=commentary,
                        model_confidence=None,  # Could be enhanced to include confidence scores
                    )
                    
                    # Store in database
                    self.db.add(headline)
                    self.db.commit()
                    results['stored'] += 1
                    
                    logger.debug(f"Stored headline: {headline_data['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing headline '{headline_data.get('title', 'Unknown')}': {e}")
                    results['errors'] += 1
                    self.db.rollback()
                    continue
            
            logger.info(f"Scraping complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in scrape_and_store_headlines: {e}")
            self.db.rollback()
            results['errors'] += 1
            return results
    
    async def scrape_all_sources(
        self, 
        max_headlines_per_source: int = 10,
        skip_existing: bool = True
    ) -> Dict[str, Dict[str, int]]:
        """
        Scrape headlines from all available sources.
        
        Args:
            max_headlines_per_source: Maximum number of headlines per source
            skip_existing: Skip headlines that already exist (by URL)
            
        Returns:
            Dictionary with results for each source
        """
        sources = ["CNBC", "Yahoo Finance", "Reuters", "MarketWatch"]
        all_results = {}
        
        for source in sources:
            logger.info(f"Scraping headlines from {source}...")
            results = await self.scrape_and_store_headlines(
                source=source,
                max_headlines=max_headlines_per_source,
                skip_existing=skip_existing
            )
            all_results[source] = results
            
        return all_results
    
    def _analyze_sentiment(self, title: str) -> tuple[str, str]:
        """Analyze sentiment of headline title."""
        try:
            return analyze_headline_sentiment(title)
        except Exception as e:
            logger.error(f"Error analyzing sentiment for '{title}': {e}")
            return "neutral", f"Sentiment analysis failed: {str(e)}"
    
    def get_recent_headlines(self, source: Optional[str] = None, limit: int = 10) -> List[Headline]:
        """Get recent headlines from the database."""
        try:
            stmt = select(Headline)
            
            if source:
                stmt = stmt.where(Headline.source == source)
            
            stmt = stmt.order_by(Headline.created_at.desc()).limit(limit)
            
            return list(self.db.execute(stmt).scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting recent headlines: {e}")
            return []
    
    def get_headlines_by_sentiment(self, sentiment: str, limit: int = 10) -> List[Headline]:
        """Get headlines filtered by sentiment."""
        try:
            stmt = select(Headline).where(Headline.sentiment == sentiment)
            stmt = stmt.order_by(Headline.created_at.desc()).limit(limit)
            
            return list(self.db.execute(stmt).scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting headlines by sentiment: {e}")
            return []
    
    def get_scraping_stats(self) -> Dict[str, int]:
        """Get statistics about scraped headlines."""
        try:
            total_headlines = self.db.execute(select(Headline)).scalars().all()
            total_count = len(total_headlines)
            
            # Count by sentiment
            positive_count = len([h for h in total_headlines if h.sentiment == 'positive'])
            negative_count = len([h for h in total_headlines if h.sentiment == 'negative'])
            neutral_count = len([h for h in total_headlines if h.sentiment == 'neutral'])
            
            # Count by source
            sources = {}
            for headline in total_headlines:
                source = headline.source
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'total_headlines': total_count,
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error getting scraping stats: {e}")
            return {}
