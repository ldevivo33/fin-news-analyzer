import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Optional
from functools import lru_cache
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialSentimentAnalyzer:
    """
    Advanced sentiment analysis model for financial news using pre-trained transformers.
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize the sentiment analyzer with a pre-trained model.
        
        Args:
            model_name: Hugging Face model name for financial sentiment analysis
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Try alternative model
            try:
                logger.info("Trying alternative model: yiyanghkust/finbert-tone")
                self.model_name = "yiyanghkust/finbert-tone"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                logger.info("Alternative model loaded successfully")
            except Exception as e2:
                logger.error(f"Failed to load alternative model: {e2}")
                # Fallback to basic model
                self.model = None
                self.tokenizer = None
    
    def predict_sentiment(self, text: str) -> Tuple[str, str, float]:
        """
        Predict sentiment using the loaded model.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (sentiment, commentary, confidence)
        """
        if self.model is None or self.tokenizer is None:
            return self._fallback_analysis(text)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                padding=True, 
                max_length=512
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                confidence = torch.max(predictions).item()
                predicted_class = torch.argmax(predictions, dim=-1).item()
            
            # Map class to sentiment - check model config for proper mapping
            if hasattr(self.model.config, 'id2label'):
                # Use model's own label mapping
                sentiment = self.model.config.id2label.get(predicted_class, "neutral").lower()
            else:
                # Default mapping for most financial models
                sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
                sentiment = sentiment_map.get(predicted_class, "neutral")
            
            # Generate commentary
            commentary = self._generate_commentary(sentiment, confidence, text)
            
            return sentiment, commentary, confidence
            
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Tuple[str, str, float]:
        """
        Enhanced fallback to rule-based analysis if model fails.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (sentiment, commentary, confidence)
        """
        text_lower = text.lower()
        
        # Comprehensive keyword lists with weights for financial sentiment
        positive_keywords = {
            # Strong positive indicators (weight 2)
            'surge': 2, 'jump': 2, 'rally': 2, 'soar': 2, 'skyrocket': 2, 'explode': 2,
            'breakthrough': 2, 'milestone': 2, 'record': 2, 'triumph': 2, 'victory': 2,
            'outperform': 2, 'exceed': 2, 'beat': 2, 'crush': 2, 'dominate': 2,
            # Moderate positive indicators (weight 1)
            'rise': 1, 'gain': 1, 'up': 1, 'positive': 1, 'strong': 1, 'profit': 1,
            'earnings': 1, 'growth': 1, 'bullish': 1, 'climb': 1, 'boost': 1,
            'optimistic': 1, 'confident': 1, 'success': 1, 'win': 1, 'high': 1,
            'improve': 1, 'increase': 1, 'expand': 1, 'thrive': 1, 'flourish': 1
        }
        
        negative_keywords = {
            # Strong negative indicators (weight 2)
            'crash': 2, 'plunge': 2, 'collapse': 2, 'meltdown': 2, 'disaster': 2,
            'crisis': 2, 'recession': 2, 'depression': 2, 'catastrophe': 2, 'devastating': 2,
            'tank': 2, 'nosedive': 2, 'freefall': 2, 'implode': 2,
            'failure': 2, 'breakdown': 2, 'ruin': 2, 'destroy': 2, 'shatter': 2,
            # Moderate negative indicators (weight 1)
            'fall': 1, 'drop': 1, 'decline': 1, 'down': 1, 'negative': 1, 'weak': 1,
            'miss': 1, 'loss': 1, 'bearish': 1, 'slump': 1, 'dip': 1, 'decrease': 1,
            'concern': 1, 'risk': 1, 'worry': 1, 'fear': 1, 'uncertainty': 1,
            'volatility': 1, 'turbulence': 1, 'pessimistic': 1, 'disappoint': 1,
            'struggle': 1, 'suffer': 1, 'bleed': 1, 'bleeding': 1
        }
        
        # Calculate weighted scores
        positive_score = sum(weight for word, weight in positive_keywords.items() if word in text_lower)
        negative_score = sum(weight for word, weight in negative_keywords.items() if word in text_lower)
        
        # Additional context analysis
        context_boost = 0
        if any(word in text_lower for word in ['earnings', 'revenue', 'profit', 'quarterly', 'annual']):
            context_boost += 0.1
        if any(word in text_lower for word in ['stock', 'shares', 'trading', 'market', 'investor']):
            context_boost += 0.1
        if any(word in text_lower for word in ['crisis', 'recession', 'crash', 'panic', 'fear']):
            context_boost += 0.2
        
        # Calculate confidence based on score strength and context
        total_score = positive_score + negative_score
        base_confidence = min(0.9, total_score * 0.05 + 0.4) if total_score > 0 else 0.5
        confidence = min(0.95, base_confidence + context_boost)
        
        # Determine sentiment with threshold
        sentiment_threshold = 0.5  # Require clear difference
        if positive_score > negative_score + sentiment_threshold:
            sentiment = "positive"
            commentary = f"Positive sentiment detected (score: {positive_score:.1f} vs {negative_score:.1f})"
        elif negative_score > positive_score + sentiment_threshold:
            sentiment = "negative"
            commentary = f"Negative sentiment detected (score: {negative_score:.1f} vs {positive_score:.1f})"
        else:
            sentiment = "neutral"
            commentary = f"Neutral sentiment - balanced indicators (pos: {positive_score:.1f}, neg: {negative_score:.1f})"
        
        return sentiment, commentary, confidence
    
    def _generate_commentary(self, sentiment: str, confidence: float, text: str) -> str:
        """
        Generate detailed commentary based on sentiment analysis results.
        
        Args:
            sentiment: Predicted sentiment
            confidence: Confidence score
            text: Original text
            
        Returns:
            Detailed commentary string
        """
        confidence_percent = round(confidence * 100, 1)
        
        if sentiment == "positive":
            base_commentary = f"Strong positive sentiment detected (confidence: {confidence_percent}%)"
        elif sentiment == "negative":
            base_commentary = f"Negative sentiment detected (confidence: {confidence_percent}%)"
        else:
            base_commentary = f"Neutral sentiment detected (confidence: {confidence_percent}%)"
        
        # Add context-specific commentary
        text_lower = text.lower()
        if any(word in text_lower for word in ['earnings', 'revenue', 'profit']):
            base_commentary += ". Financial performance indicators present."
        if any(word in text_lower for word in ['stock', 'shares', 'trading']):
            base_commentary += ". Market-related content identified."
        if any(word in text_lower for word in ['crisis', 'recession', 'crash']):
            base_commentary += ". High-impact financial terms detected."
        
        return base_commentary

# Global model instance
_analyzer_instance = None

def get_analyzer() -> FinancialSentimentAnalyzer:
    """Get or create the global analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = FinancialSentimentAnalyzer()
    return _analyzer_instance

@lru_cache(maxsize=1024)
def analyze_headline_sentiment(headline: str) -> tuple[str, str]:
    """
    Analyze financial headline sentiment using the advanced model.

    Results are cached (LRU, max 1024 entries) to reduce inference latency
    for repeated headlines.

    Args:
        headline: Financial news headline to analyze

    Returns:
        Tuple of (sentiment, commentary)
    """
    analyzer = get_analyzer()
    sentiment, commentary, confidence = analyzer.predict_sentiment(headline)

    # Add confidence to commentary
    confidence_percent = round(confidence * 100, 1)
    commentary += f" (Model confidence: {confidence_percent}%)"

    return sentiment, commentary