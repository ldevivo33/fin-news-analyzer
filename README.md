# Financial News Sentiment Analyzer

WEB ACCESS @ https://finnewsanalyzer.site/

A FastAPI-based web service that analyzes the sentiment of financial news headlines by leveraging AI.

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy 2.x, SQLite
- ML: PyTorch, Transformers (FinBERT)
- Frontend: Vanilla HTML/CSS/JavaScript
- CI/CD: GitHub Actions (lint + test)
- Testing: pytest, ruff

## How It Works
- Advanced AI (FinBERT) used for sentiment; falls back to a financial keyword-based analyzer if model loading fails.
- Confidence scoring included in commentary.
- Headlines can be stored in a SQLite DB for retrieval and filtering.
- LRU caching on inference reduces latency for repeated headlines.

## Deployment

The application is currently deployed on AWS EC2 with the following production setup:

### Infrastructure
- **Server**: AWS EC2 Ubuntu 22.04 instance
- **Domain**: Custom domain managed via Squarespace (finnewsanalyzer.site)
- **SSL**: Let's Encrypt HTTPS with auto-renewal
- **Reverse Proxy**: Nginx for SSL termination and static file serving
- **Process Management**: systemd for 24/7 uptime and auto-restart
- **Security**: AWS Security Groups (only ports 22/80/443 open)

### Production Stack
- **Backend**: FastAPI + Uvicorn (managed by systemd)
- **Frontend**: Static files served by Nginx
- **Database**: SQLite (backend/finnews.db)
- **SSL Certificate**: Let's Encrypt (auto-renewal configured)
- **DNS**: Elastic IP with A-records pointing to EC2 instance

### Access
- **Production URL**: https://finnewsanalyzer.site/
- **Status**: Live and operational 24/7

### Database & Performance
- **Storage Capacity**: Can handle hundreds of thousands of headlines (SQLite database)
- **Query Limits**: 100 headlines per request (pagination support)
- **Performance**: Optimized for up to 100K+ headlines with good response times

## What's Next?

Potential future enhancements:
- Advanced filtering and search capabilities
- Historical trend analysis
- PostgreSQL for cloud-native database
- Docker Compose production setup
