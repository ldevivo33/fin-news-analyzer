import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class BaseScraper:
    """Base scraper class with common functionality."""
    
    def __init__(self, base_url: str, news_url: str, source_name: str):
        self.base_url = base_url
        self.news_url = news_url
        self.source_name = source_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def scrape_headlines(self, max_headlines: int = 20) -> List[Dict[str, str]]:
        """Scrape headlines from the news page."""
        headlines = []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(self.news_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                headlines = self._extract_headlines(soup, max_headlines)
                
                logger.info(f"Successfully scraped {len(headlines)} headlines from {self.source_name}")
                
        except httpx.RequestError as e:
            logger.error(f"Request error scraping {self.source_name}: {e}")
        except Exception as e:
            logger.error(f"Error scraping {self.source_name} headlines: {e}")
            
        return headlines
    
    def _extract_headlines(self, soup: BeautifulSoup, max_headlines: int) -> List[Dict[str, str]]:
        """Extract headlines from parsed HTML - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _extract_headlines")
    
    def _extract_headline_data(self, element, title: str, href: str) -> Optional[Dict[str, str]]:
        """Extract headline data from a single element."""
        try:
            if not title or len(title) < 10:  # Skip very short titles
                return None
                
            if not href:
                return None
                
            # Make URL absolute
            url = urljoin(self.base_url, href)
            
            # Skip non-article URLs
            if not self._is_article_url(url):
                return None
            
            # Try to extract published date
            published_at = self._extract_published_date(url, element)
            
            return {
                'title': title.strip(),
                'url': url,
                'published_at': published_at,
                'source': self.source_name
            }
            
        except Exception as e:
            logger.debug(f"Error extracting headline data: {e}")
            return None
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _is_article_url")
    
    def _extract_published_date(self, url: str, element) -> Optional[str]:
        """Extract published date from URL or element."""
        # Try to extract date from URL first
        date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            try:
                dt = datetime(int(year), int(month), int(day))
                return dt.isoformat()
            except ValueError:
                pass
        
        # Try to find date in element or nearby elements
        time_element = element.find_parent().find('time') if element.find_parent() else None
        if time_element and time_element.get('datetime'):
            return time_element.get('datetime')
        
        # Default to current time if no date found
        return datetime.now().isoformat()
    
    def _is_valid_headline(self, headline_data: Dict[str, str]) -> bool:
        """Validate headline data."""
        title = headline_data.get('title', '')
        url = headline_data.get('url', '')
        
        if not title or not url:
            return False
            
        if len(title) < 15 or len(title) > 200:
            return False
            
        # Skip titles that look like navigation or ads
        skip_patterns = [
            r'^(Subscribe|Sign|Login|Register|Menu|Search)',
            r'^(Watch|Listen|Read|More)',
            r'^(Yahoo|CNBC|Reuters|MarketWatch|Pro|Club)',
            r'^(Markets|Business|Investing|Tech|Politics)',
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return False
                
        return True


class CNBCScraper(BaseScraper):
    """Scraper for CNBC Finance headlines."""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.cnbc.com",
            news_url="https://www.cnbc.com/finance/",
            source_name="CNBC"
        )
    
    def _extract_headlines(self, soup: BeautifulSoup, max_headlines: int) -> List[Dict[str, str]]:
        """Extract headlines from parsed HTML."""
        headlines = []
        
        # CNBC uses various selectors for headlines - try multiple approaches
        selectors = [
            'a[data-module="ArticleLink"]',  # Main article links
            'a[href*="/2025/"]',  # Links with year in URL (current year)
            '.ArticleWrap a',  # Article wrapper links
            '.RiverHeadline a',  # River headline links
            'h2 a',  # Headline links in h2 tags
            'h3 a',  # Headline links in h3 tags
        ]
        
        for selector in selectors:
            if len(headlines) >= max_headlines:
                break
                
            elements = soup.select(selector)
            
            for element in elements:
                if len(headlines) >= max_headlines:
                    break
                    
                title = element.get_text(strip=True)
                href = element.get('href', '')
                
                headline_data = self._extract_headline_data(element, title, href)
                if headline_data and self._is_valid_headline(headline_data):
                    headlines.append(headline_data)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_headlines = []
        for headline in headlines:
            if headline['url'] not in seen_urls:
                seen_urls.add(headline['url'])
                unique_headlines.append(headline)
        
        return unique_headlines[:max_headlines]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article."""
        # CNBC article URLs typically contain date patterns
        article_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # /2025/09/17/
            r'/\d{4}/\d{1,2}/\d{1,2}/',  # /2025/9/17/
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url):
                return True
                
        # Also check for common article indicators
        article_indicators = ['/finance/', '/business/', '/markets/', '/investing/']
        return any(indicator in url for indicator in article_indicators)


class YahooFinanceScraper(BaseScraper):
    """Scraper for Yahoo Finance headlines."""
    
    def __init__(self):
        super().__init__(
            base_url="https://finance.yahoo.com",
            news_url="https://finance.yahoo.com/news/",
            source_name="Yahoo Finance"
        )
    
    def _extract_headlines(self, soup: BeautifulSoup, max_headlines: int) -> List[Dict[str, str]]:
        """Extract headlines from Yahoo Finance."""
        headlines = []
        
        # Yahoo Finance selectors
        selectors = [
            'h3 a',  # Main headline links
            'h2 a',  # Secondary headline links
            '.js-content-viewer a',  # Content viewer links
            '[data-module="ArticleItem"] a',  # Article item links
            '.Ov(h) a',  # Overflow hidden links
            'a[href*="/news/"]',  # News links
        ]
        
        for selector in selectors:
            if len(headlines) >= max_headlines:
                break
                
            elements = soup.select(selector)
            
            for element in elements:
                if len(headlines) >= max_headlines:
                    break
                    
                title = element.get_text(strip=True)
                href = element.get('href', '')
                
                headline_data = self._extract_headline_data(element, title, href)
                if headline_data and self._is_valid_headline(headline_data):
                    headlines.append(headline_data)
        
        # Remove duplicates
        seen_urls = set()
        unique_headlines = []
        for headline in headlines:
            if headline['url'] not in seen_urls:
                seen_urls.add(headline['url'])
                unique_headlines.append(headline)
        
        return unique_headlines[:max_headlines]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article."""
        # Yahoo Finance article patterns
        article_patterns = [
            r'/news/[^/]+-',  # /news/headline-
            r'/news/\d{4}-\d{2}-\d{2}',  # /news/2025-09-17
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url):
                return True
                
        return '/news/' in url and len(url.split('/')) > 4


class ReutersScraper(BaseScraper):
    """Scraper for Reuters Markets headlines."""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.reuters.com",
            news_url="https://www.reuters.com/markets/",
            source_name="Reuters"
        )
    
    def _extract_headlines(self, soup: BeautifulSoup, max_headlines: int) -> List[Dict[str, str]]:
        """Extract headlines from Reuters Markets."""
        headlines = []
        
        # Reuters selectors
        selectors = [
            'a[data-testid="Link"]',  # Reuters link elements
            'h3 a',  # Headline links
            'h2 a',  # Secondary headlines
            '.media-story-card a',  # Media story cards
            '.story-card a',  # Story cards
            'a[href*="/business/"]',  # Business links
            'a[href*="/markets/"]',  # Markets links
        ]
        
        for selector in selectors:
            if len(headlines) >= max_headlines:
                break
                
            elements = soup.select(selector)
            
            for element in elements:
                if len(headlines) >= max_headlines:
                    break
                    
                title = element.get_text(strip=True)
                href = element.get('href', '')
                
                headline_data = self._extract_headline_data(element, title, href)
                if headline_data and self._is_valid_headline(headline_data):
                    headlines.append(headline_data)
        
        # Remove duplicates
        seen_urls = set()
        unique_headlines = []
        for headline in headlines:
            if headline['url'] not in seen_urls:
                seen_urls.add(headline['url'])
                unique_headlines.append(headline)
        
        return unique_headlines[:max_headlines]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article."""
        # Reuters article patterns
        article_patterns = [
            r'/business/[^/]+-',  # /business/headline-
            r'/markets/[^/]+-',  # /markets/headline-
            r'/\d{4}/\d{2}/\d{2}/',  # /2025/09/17/
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url):
                return True
                
        return any(indicator in url for indicator in ['/business/', '/markets/'])


class MarketWatchScraper(BaseScraper):
    """Scraper for MarketWatch headlines."""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.marketwatch.com",
            news_url="https://www.marketwatch.com/latest-news",
            source_name="MarketWatch"
        )
    
    def _extract_headlines(self, soup: BeautifulSoup, max_headlines: int) -> List[Dict[str, str]]:
        """Extract headlines from MarketWatch."""
        headlines = []
        
        # MarketWatch selectors
        selectors = [
            'h3 a',  # Main headlines
            'h2 a',  # Secondary headlines
            '.article__headline a',  # Article headlines
            '.link',  # Link elements
            'a[href*="/story/"]',  # Story links
            'a[href*="/article/"]',  # Article links
        ]
        
        for selector in selectors:
            if len(headlines) >= max_headlines:
                break
                
            elements = soup.select(selector)
            
            for element in elements:
                if len(headlines) >= max_headlines:
                    break
                    
                title = element.get_text(strip=True)
                href = element.get('href', '')
                
                headline_data = self._extract_headline_data(element, title, href)
                if headline_data and self._is_valid_headline(headline_data):
                    headlines.append(headline_data)
        
        # Remove duplicates
        seen_urls = set()
        unique_headlines = []
        for headline in headlines:
            if headline['url'] not in seen_urls:
                seen_urls.add(headline['url'])
                unique_headlines.append(headline)
        
        return unique_headlines[:max_headlines]
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article."""
        # MarketWatch article patterns
        article_patterns = [
            r'/story/',  # /story/headline
            r'/article/',  # /article/headline
            r'/\d{4}/\d{2}/\d{2}/',  # /2025/09/17/
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url):
                return True
                
        return any(indicator in url for indicator in ['/story/', '/article/'])


# Convenience functions for easy importing
async def scrape_cnbc_headlines(max_headlines: int = 20) -> List[Dict[str, str]]:
    """Scrape CNBC Finance headlines."""
    scraper = CNBCScraper()
    return await scraper.scrape_headlines(max_headlines)

async def scrape_yahoo_finance_headlines(max_headlines: int = 20) -> List[Dict[str, str]]:
    """Scrape Yahoo Finance headlines."""
    scraper = YahooFinanceScraper()
    return await scraper.scrape_headlines(max_headlines)

async def scrape_reuters_headlines(max_headlines: int = 20) -> List[Dict[str, str]]:
    """Scrape Reuters Markets headlines."""
    scraper = ReutersScraper()
    return await scraper.scrape_headlines(max_headlines)

async def scrape_marketwatch_headlines(max_headlines: int = 20) -> List[Dict[str, str]]:
    """Scrape MarketWatch headlines."""
    scraper = MarketWatchScraper()
    return await scraper.scrape_headlines(max_headlines)