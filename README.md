# Financial News Sentiment Analyzer

WEB ACCESS @ https://finnewsanalyzer.site/

A FastAPI-based web service that analyzes the sentiment of financial news headlines by leveraging AI and machine learning insights.

### Prerequisites
- Python (3.8 or higher)
- pip (Python package installer)

### Install & Run
0. **Navigate to the project root folder**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the Frontend UI:**
   http://localhost:8000

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy 2.x, SQLite
- ML: PyTorch, Transformers (FinBERT)
- Frontend: Vanilla HTML/CSS/JavaScript

## How It Works
- Advanced AI (FinBERT) used for sentiment; falls back to a financial keyword-based analyzer if model loading fails.
- Confidence scoring included in commentary.
- Headlines can be stored in a local SQLite DB for retrieval and filtering.

## Features

- **Sandbox Mode** To experiment with the model instantly. 
- **Live Web Scraping** From 4 free to access sources (CNBC, Yahoo Finance, Reuters, MarketWatch)
- **Trend Analysys** coming soon...
- **Stored Headlines section** To add test headlines (auto-analyzed on insert), view sentiment, commentary, source, and dates. Filter and search available.
- **Works on any device locally** - phone, tablet, desktop with a stylish black/white UI with subtle market inspired visuals.

## Project Structure

fin-news-analyzer/
├── app/
│ ├── main.py # FastAPI server + endpoints
│ ├── models.py # FinBERT analyzer + fallback
│ ├── schema.py # Pydantic schemas
│ ├── db.py # SQLAlchemy engine/session/Base
│ └── db_models.py # ORM models (Headline)
| └── scraper_service.py
| └── scraper.py
├── backend/
│ └── finnews.db # SQLite database (auto-created)
├── frontend/
│ └── index.html # UI (Sandbox + Stored Headlines)
├── requirements.txt
└── README.md

## Database
- SQLite file: `backend/finnews.db` (created automatically on startup)
- ORM: SQLAlchemy 2.x Declarative (sync)
- Session: Session-per-request dependency
- Migrations: None (tables created on startup)

### Headline Model
- id, source, title, url, published_at, raw_text
- sentiment, commentary, model_confidence
- created_at, updated_at
- Historical duplicates allowed
- Sentiment computed on first insert

## API Endpoints
- GET `/` — Serves the frontend UI
- GET `/health` — Health check

- POST `/analyze`
  - Request: `{ "headline": "Your text here" }`
  - Response: `{ "sentiment": "positive|neutral|negative", "commentary": "..." }`

- POST `/headlines`
  - Request:
    ```
    {
      "source": "Reuters",
      "title": "Apple stock surges 5% on strong earnings",
      "url": "https://example.com/article",
      "published_at": "2025-09-11T12:00:00",
      "raw_text": null
    }
    ```
  - Behavior: Computes sentiment on insert and stores the record.
  - Response: Full stored headline (including id, sentiment, commentary).

- GET `/headlines`
  - Query params (optional):
    - `source` — filter by source
    - `sentiment` — positive|neutral|negative
    - `q` — search in title
    - `start_date`, `end_date` — ISO8601
    - `limit` (default 20, max 100), `offset` (default 0)
  - Response: `{ "items": [...], "total": N }`
  - Default sort: `published_at DESC`, then `created_at DESC`

- GET `/headlines/{id}`
  - Response: Full stored headline

## Frontend Usage
- Sandbox Mode:
  - Enter a headline and click “Analyze Sentiment” to test the Advanced AI model.
  - Inline validation for empty inputs; no browser popups.
- Stored Headlines:
  - Add test headlines (Source, URL, Headline).
  - View and filter existing records by source, sentiment, and search term.
  - Graceful empty/error states and loading spinners.

## Troubleshooting
- First run may be slow due to FinBERT model download.
- If `/headlines` is empty, add a test headline using the form or POST endpoint.
- SQLite file is created at `backend/finnews.db`. Ensure the process has write permissions.

## What's Next?

I am currently working on the following features currently and will ship ASAP:
- Web up time consistency and security
- Scraping logs
- Historical analysis & trends
