"""
Sentiment Analysis Engine
Combines multiple sentiment analysis libraries for robust analysis
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer as NLTKSentimentIntensityAnalyzer
from loguru import logger

from src.models.news_article import (
    SentimentAnalysis, 
    SentimentEngine, 
    SentimentLabel
)

class SentimentAnalyzer:
    """Multi-engine sentiment analyzer"""
    
    def __init__(self):
        """Initialize sentiment analyzers"""
        self.textblob_analyzer = None
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.nltk_analyzer = None
        
        # Download required NLTK data
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            self.nltk_analyzer = NLTKSentimentIntensityAnalyzer()
        except Exception as e:
            logger.warning(f"Failed to initialize NLTK analyzer: {e}")
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\']', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction based on frequency
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:max_keywords]]
    
    def analyze_with_textblob(self, text: str) -> Optional[SentimentAnalysis]:
        """Analyze sentiment using TextBlob"""
        try:
            if not text:
                return None
            
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                return None
            
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment label
            if polarity > 0.1:
                sentiment_label = SentimentLabel.POSITIVE
            elif polarity < -0.1:
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.NEUTRAL
            
            # Extract keywords
            keywords = self.extract_keywords(cleaned_text)
            
            return SentimentAnalysis(
                engine=SentimentEngine.TEXTBLOB,
                sentiment_score=polarity,
                sentiment_label=sentiment_label,
                confidence_score=1.0 - abs(subjectivity - 0.5) * 2,  # Convert subjectivity to confidence
                keywords=keywords,
                additional_data={
                    'subjectivity': subjectivity,
                    'word_count': len(cleaned_text.split())
                }
            )
            
        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return None
    
    def analyze_with_vader(self, text: str) -> Optional[SentimentAnalysis]:
        """Analyze sentiment using VADER"""
        try:
            if not text:
                return None
            
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                return None
            
            scores = self.vader_analyzer.polarity_scores(cleaned_text)
            compound_score = scores['compound']
            
            # Determine sentiment label
            if compound_score > 0.1:
                sentiment_label = SentimentLabel.POSITIVE
            elif compound_score < -0.1:
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.NEUTRAL
            
            # Extract keywords
            keywords = self.extract_keywords(cleaned_text)
            
            return SentimentAnalysis(
                engine=SentimentEngine.VADER,
                sentiment_score=compound_score,
                sentiment_label=sentiment_label,
                confidence_score=abs(compound_score),  # Use absolute value as confidence
                keywords=keywords,
                additional_data={
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu'],
                    'word_count': len(cleaned_text.split())
                }
            )
            
        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return None
    
    def analyze_with_nltk(self, text: str) -> Optional[SentimentAnalysis]:
        """Analyze sentiment using NLTK"""
        try:
            if not text or not self.nltk_analyzer:
                return None
            
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                return None
            
            scores = self.nltk_analyzer.polarity_scores(cleaned_text)
            compound_score = scores['compound']
            
            # Determine sentiment label
            if compound_score > 0.1:
                sentiment_label = SentimentLabel.POSITIVE
            elif compound_score < -0.1:
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.NEUTRAL
            
            # Extract keywords
            keywords = self.extract_keywords(cleaned_text)
            
            return SentimentAnalysis(
                engine=SentimentEngine.NLTK,
                sentiment_score=compound_score,
                sentiment_label=sentiment_label,
                confidence_score=abs(compound_score),  # Use absolute value as confidence
                keywords=keywords,
                additional_data={
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu'],
                    'word_count': len(cleaned_text.split())
                }
            )
            
        except Exception as e:
            logger.error(f"NLTK analysis failed: {e}")
            return None
    
    def analyze_text(self, text: str, engines: List[SentimentEngine] = None) -> List[SentimentAnalysis]:
        """Analyze text using multiple engines"""
        if not text:
            return []
        
        if engines is None:
            engines = [SentimentEngine.TEXTBLOB, SentimentEngine.VADER, SentimentEngine.NLTK]
        
        results = []
        
        for engine in engines:
            try:
                if engine == SentimentEngine.TEXTBLOB:
                    result = self.analyze_with_textblob(text)
                elif engine == SentimentEngine.VADER:
                    result = self.analyze_with_vader(text)
                elif engine == SentimentEngine.NLTK:
                    result = self.analyze_with_nltk(text)
                else:
                    logger.warning(f"Unknown sentiment engine: {engine}")
                    continue
                
                if result:
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Analysis failed for engine {engine}: {e}")
                continue
        
        logger.info(f"Completed sentiment analysis with {len(results)} engines")
        return results
    
    def get_consensus_sentiment(self, analyses: List[SentimentAnalysis]) -> Optional[Dict[str, Any]]:
        """Get consensus sentiment from multiple analyses"""
        if not analyses:
            return None
        
        # Calculate average sentiment score
        scores = [analysis.sentiment_score for analysis in analyses]
        avg_score = sum(scores) / len(scores)
        
        # Determine consensus label
        labels = [analysis.sentiment_label for analysis in analyses]
        positive_count = labels.count(SentimentLabel.POSITIVE)
        negative_count = labels.count(SentimentLabel.NEGATIVE)
        neutral_count = labels.count(SentimentLabel.NEUTRAL)
        
        max_count = max(positive_count, negative_count, neutral_count)
        
        if positive_count == max_count:
            consensus_label = SentimentLabel.POSITIVE
        elif negative_count == max_count:
            consensus_label = SentimentLabel.NEGATIVE
        else:
            consensus_label = SentimentLabel.NEUTRAL
        
        # Calculate confidence based on agreement
        agreement_ratio = max_count / len(analyses)
        
        return {
            'avg_sentiment_score': avg_score,
            'consensus_label': consensus_label,
            'confidence_score': agreement_ratio,
            'engine_count': len(analyses),
            'positive_votes': positive_count,
            'negative_votes': negative_count,
            'neutral_votes': neutral_count
        }
    
    def analyze_article(self, title: str, content: str = None, engines: List[SentimentEngine] = None) -> List[SentimentAnalysis]:
        """Analyze a news article"""
        # Combine title and content for analysis
        text = title
        if content:
            text += " " + content
        
        return self.analyze_text(text, engines) 