from pydantic import BaseModel
from typing import Optional

# Define a Pydantic model for the request body:
#   - headline: string
class HeadlineRequest(BaseModel):
    headline: str
    
    # Add validation - headlines shouldn't be empty
    class Config:
        schema_extra = {
            "example": {
                "headline": "Apple stock surges 5% on strong earnings report"
            }
        }

# Define Pydantic model for the response body: 
#   - sentiment: string ("positive", "negative", "neutral")
#   - commentary: string(optional placeholder text)
class SentimentResponse(BaseModel):
    sentiment: str  # "positive", "negative", "neutral"
    commentary: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "sentiment": "positive",
                "commentary": "This headline indicates strong positive sentiment with keywords like 'surges' and 'strong earnings'"
            }
        }