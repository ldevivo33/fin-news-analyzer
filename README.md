# Financial News Sentiment Analyzer

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

**Backend:**
- FastAPI - Modern Python web framework
- PyTorch + Transformers - ML model for sentiment analysis
- Pydantic - Data validation

**Frontend:**
- Vanilla HTML/CSS/JavaScript - No frameworks needed


## 🔧 How It Works

### How It Works
The app uses a smart two-tier approach:

1. **ML Model First**: Tries to use FinBERT (a financial AI model) for accurate predictions
2. **Smart Fallback**: If the AI model fails, it falls back to enhanced keyword analysis
3. **Confidence Scoring**: Shows how confident the model is in its prediction
4. **Financial Context**: Understands market-specific language and terminology

### What You'll See
1. **Enter a headline** like "Apple stock surges 5% on strong earnings"
2. **Click analyze** and watch the magic happen
3. **Get instant results** with color-coded sentiment (green=positive, red=negative, white=neutral)
4. **See detailed commentary** explaining why the AI made that decision

## Features

**What makes this special:**
- **Beautiful black & white design** with professional typography
- **Tasteful inancial chart backgrounds** that resemble trading screens
- **AI-powered analysis** that actually understands financial language
- **Instant results** - no waiting, no loading screens
- **Works on any device** - phone, tablet, desktop
- **No scrolling needed** - everything fits on one screen


## API Endpoints

If you want to use this programmatically:
- `GET /` - The main frontend interface
- `POST /analyze` - Send a headline, get sentiment back
- `GET /health` - Check if the server is running

## Project Structure
```
fin-news-analyzer/
├── app/
│   ├── main.py          # FastAPI server
│   ├── models.py        # AI sentiment analysis
│   └── schema.py        # Data validation
├── frontend/
│   └── index.html       # The beautiful UI
├── requirements.txt     # What to install
└── README.md           # This file
```

## Troubleshooting

**If the server won't start:**
- Make sure Python is installed: `python --version`
- Try different commands: `python3 -m uvicorn` or `py -m uvicorn`
- Check if port 8000 is already in use

**If the AI model is slow:**
- First run takes longer (downloading the model)
- Subsequent runs are instant
- Check your internet connection for model download

## What's Next?

This is just the beginning, I am working on the following features currently and will ship ASAP:
- Web Deployment
- Web scraping to get real headlines automatically
- Historical analysis and trends
- Email alerts for sentiment changes
- Integration with trading platforms
- More sophisticated AI models 
