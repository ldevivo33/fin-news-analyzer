# Financial News Sentiment Analyzer

A FastAPI-based web service that analyzes the sentiment of financial news headlines using rule-based keyword analysis.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Install & Run
0. **Navigate to the project root folder**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app/main.py
   ```

3. **Access the API:**
   - API will be available at: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## 📚 Learning Concepts

### FastAPI Fundamentals
- **FastAPI**: A modern, fast web framework for building APIs with Python
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI applications

### Key Components Explained

#### 1. **Pydantic Models** (`HeadlineRequest` & `SentimentResponse`)
```python
class HeadlineRequest(BaseModel):
    headline: str
```
- **Purpose**: Define the structure of incoming requests and outgoing responses
- **Validation**: Automatically validates data types and formats
- **Documentation**: Provides examples for API documentation

#### 2. **API Endpoints**
```python
@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: HeadlineRequest):
```
- **Decorators**: `@app.post()` defines HTTP POST method
- **Async/Await**: Enables non-blocking I/O operations
- **Type Hints**: Ensures type safety and better IDE support

#### 3. **Error Handling**
```python
try:
    # Your logic here
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```
- **HTTPException**: Proper HTTP error responses
- **Status Codes**: Standard HTTP status codes (200, 400, 500, etc.)

## 🔧 How It Works

### Current Implementation (Rule-Based)
The current version uses a simple keyword-based approach:

1. **Keyword Lists**: Predefined positive/negative financial terms
2. **Text Processing**: Convert to lowercase for case-insensitive matching
3. **Counting**: Count occurrences of positive vs negative keywords
4. **Decision Logic**: Compare counts to determine sentiment

### Example Usage

**Request:**
```json
{
  "headline": "Apple stock surges 5% on strong earnings report"
}
```

**Response:**
```json
{
  "sentiment": "positive",
  "commentary": "Positive sentiment detected with 2 positive keywords"
}
```

## 🧠 Next Steps for ML Integration

### 1. **Data Collection**
- Gather financial headlines with sentiment labels
- Create training dataset with balanced classes

### 2. **Feature Engineering**
- Text preprocessing (tokenization, stemming)
- TF-IDF or word embeddings
- Financial-specific features (company names, numbers, percentages)

### 3. **Model Selection**
- **Traditional ML**: Random Forest, SVM, Logistic Regression
- **Deep Learning**: LSTM, BERT, Transformers
- **Pre-trained Models**: FinBERT (financial BERT)

### 4. **Model Training**
```python
# Example with scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

vectorizer = TfidfVectorizer()
classifier = RandomForestClassifier()
```

### 5. **Integration**
- Replace `analyze_headline_sentiment()` function
- Add model loading and prediction
- Implement confidence scores

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/analyze` | Analyze headline sentiment |

## 🛠️ Development

### Project Structure
```
fin-news-analyzer/
├── app/
│   └── main.py          # Main FastAPI application
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

### Testing the API
You can test the API using:
- **Web Interface**: Visit http://localhost:8000/docs
- **curl**: `curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d '{"headline": "Tesla stock falls on weak earnings"}`
- **Python requests**:
  ```python
  import requests
  
  response = requests.post(
      "http://localhost:8000/analyze",
      json={"headline": "Apple stock surges 5% on strong earnings report"}
  )
  print(response.json())
  ```

## 🎯 Learning Goals

This project teaches you:
- **API Development**: Building RESTful APIs with FastAPI
- **Data Validation**: Using Pydantic for request/response validation
- **Error Handling**: Proper HTTP error responses
- **Documentation**: Auto-generated API docs
- **Text Processing**: Basic NLP concepts
- **Machine Learning**: Foundation for ML integration

## 🔮 Future Enhancements

1. **ML Model Integration**: Replace rule-based with trained models
2. **Database**: Store analysis results and headlines
3. **Authentication**: API key management
4. **Rate Limiting**: Prevent abuse
5. **Caching**: Improve performance
6. **Monitoring**: Logging and metrics
7. **Testing**: Unit and integration tests
8. **Deployment**: Docker containerization 