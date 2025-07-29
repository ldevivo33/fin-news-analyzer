def analyze_headline_sentiment(headline: str) -> tuple[str, str]:
    """
    Simple rule-based sentiment analysis for financial headlines.
    
    This is a basic implementation - in a real project, you'd use ML models!
    """
    headline_lower = headline.lower()
    
    # Define positive and negative keywords for financial news
    positive_keywords = [
        'surge', 'jump', 'rise', 'gain', 'up', 'positive', 'strong', 'beat', 'exceed',
        'profit', 'earnings', 'growth', 'bullish', 'rally', 'soar', 'climb', 'boost'
    ]
    
    negative_keywords = [
        'fall', 'drop', 'decline', 'down', 'negative', 'weak', 'miss', 'loss',
        'crash', 'plunge', 'bearish', 'slump', 'dip', 'decrease', 'concern', 'risk'
    ]
    
    # Count positive and negative keywords
    positive_count = sum(1 for word in positive_keywords if word in headline_lower)
    negative_count = sum(1 for word in negative_keywords if word in headline_lower)
    
    # Determine sentiment
    if positive_count > negative_count:
        sentiment = "positive"
        commentary = f"Positive sentiment detected with {positive_count} positive keywords"
    elif negative_count > positive_count:
        sentiment = "negative"
        commentary = f"Negative sentiment detected with {negative_count} negative keywords"
    else:
        sentiment = "neutral"
        commentary = "Neutral sentiment - balanced or no clear sentiment indicators"
    
    return sentiment, commentary