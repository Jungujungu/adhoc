"""
News Article Data Model
Defines the structure for news articles and sentiment analysis results
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class SentimentLabel(str, Enum):
    """Sentiment label enumeration"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentEngine(str, Enum):
    """Sentiment analysis engine enumeration"""
    TEXTBLOB = "textblob"
    VADER = "vader"
    NLTK = "nltk"

class NewsArticle(BaseModel):
    """News article data model"""
    
    # Article metadata
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = Field(None, max_length=10000)
    url: Optional[str] = Field(None, max_length=1000)
    source: str = Field(..., min_length=1, max_length=100)
    published_date: Optional[datetime] = None
    scraped_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Company association
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    ticker: Optional[str] = None
    
    # Article ID (for database)
    article_id: Optional[int] = None
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('title')
    def clean_title(cls, v):
        """Clean and normalize title"""
        return v.strip() if v else v
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SentimentAnalysis(BaseModel):
    """Sentiment analysis result model"""
    
    # Analysis metadata
    engine: SentimentEngine
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_label: SentimentLabel
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Keywords and additional data
    keywords: Optional[List[str]] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    # Database fields
    sentiment_id: Optional[int] = None
    article_id: Optional[int] = None
    company_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('sentiment_label')
    def validate_sentiment_label(cls, v, values):
        """Validate sentiment label based on score"""
        score = values.get('sentiment_score', 0)
        
        if score > 0.1:
            expected_label = SentimentLabel.POSITIVE
        elif score < -0.1:
            expected_label = SentimentLabel.NEGATIVE
        else:
            expected_label = SentimentLabel.NEUTRAL
            
        if v != expected_label:
            # Log warning but don't raise error
            print(f"Warning: Sentiment label {v} doesn't match score {score}")
            
        return v
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NewsArticleWithSentiment(BaseModel):
    """Combined news article with sentiment analysis"""
    
    article: NewsArticle
    sentiment_analyses: List[SentimentAnalysis] = []
    
    def get_average_sentiment(self) -> Optional[float]:
        """Get average sentiment score across all engines"""
        if not self.sentiment_analyses:
            return None
        
        scores = [sa.sentiment_score for sa in self.sentiment_analyses]
        return sum(scores) / len(scores)
    
    def get_consensus_label(self) -> Optional[SentimentLabel]:
        """Get consensus sentiment label"""
        if not self.sentiment_analyses:
            return None
        
        labels = [sa.sentiment_label for sa in self.sentiment_analyses]
        positive_count = labels.count(SentimentLabel.POSITIVE)
        negative_count = labels.count(SentimentLabel.NEGATIVE)
        neutral_count = labels.count(SentimentLabel.NEUTRAL)
        
        max_count = max(positive_count, negative_count, neutral_count)
        
        if positive_count == max_count:
            return SentimentLabel.POSITIVE
        elif negative_count == max_count:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL
    
    def get_confidence_score(self) -> Optional[float]:
        """Get average confidence score"""
        if not self.sentiment_analyses:
            return None
        
        scores = [sa.confidence_score for sa in self.sentiment_analyses if sa.confidence_score]
        return sum(scores) / len(scores) if scores else None

class DailySentimentSummary(BaseModel):
    """Daily sentiment summary for a company"""
    
    company_id: int
    company_name: str
    ticker: str
    date: datetime
    avg_sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_label: SentimentLabel
    article_count: int = Field(..., ge=0)
    positive_count: int = Field(..., ge=0)
    negative_count: int = Field(..., ge=0)
    neutral_count: int = Field(..., ge=0)
    
    # Database fields
    summary_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('sentiment_label')
    def validate_summary_sentiment_label(cls, v, values):
        """Validate sentiment label based on average score"""
        score = values.get('avg_sentiment_score', 0)
        
        if score > 0.1:
            expected_label = SentimentLabel.POSITIVE
        elif score < -0.1:
            expected_label = SentimentLabel.NEGATIVE
        else:
            expected_label = SentimentLabel.NEUTRAL
            
        if v != expected_label:
            print(f"Warning: Summary sentiment label {v} doesn't match score {score}")
            
        return v
    
    @validator('article_count')
    def validate_article_counts(cls, v, values):
        """Validate that article counts are reasonable"""
        positive = values.get('positive_count', 0)
        negative = values.get('negative_count', 0)
        neutral = values.get('neutral_count', 0)
        
        # Article count should be >= sum of sentiment counts (since each article can have multiple sentiment analyses)
        sentiment_total = positive + negative + neutral
        if v < sentiment_total:
            raise ValueError(f'Article count {v} is less than sum of sentiment counts {sentiment_total}')
        
        return v
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 