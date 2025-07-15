"""
Snowflake Database Manager
Handles Snowflake database connections and operations
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
from loguru import logger

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.snowflake_config import SnowflakeConfig, get_all_setup_queries
from src.models.news_article import (
    NewsArticle, 
    SentimentAnalysis, 
    NewsArticleWithSentiment,
    DailySentimentSummary
)

class SnowflakeManager:
    """Manages Snowflake database operations"""
    
    def __init__(self):
        """Initialize Snowflake manager"""
        self.config = SnowflakeConfig()
        self.connection = None
        self.engine = None
        
        if not self.config.validate_config():
            raise ValueError("Invalid Snowflake configuration. Check your environment variables.")
    
    def connect(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                **self.config.get_connection_params()
            )
            
            # Create SQLAlchemy engine for pandas operations
            self.engine = create_engine(self.config.get_connection_string())
            
            logger.info("Successfully connected to Snowflake")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return False
    
    def disconnect(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Snowflake")
        
        if self.engine:
            self.engine.dispose()
    
    def setup_database(self) -> bool:
        """Setup database tables and views"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Execute all setup queries
            for query in get_all_setup_queries():
                cursor.execute(query)
                logger.debug(f"Executed query: {query[:100]}...")
            
            cursor.close()
            logger.info("Database setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    def insert_company(self, company_data: Dict[str, Any]) -> Optional[int]:
        """Insert a company into the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO COMPANIES (rank, name, ticker, sector)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                company_data['rank'],
                company_data['name'],
                company_data['ticker'],
                company_data['sector']
            ))
            # Fetch the company_id by ticker (unique)
            cursor.execute("SELECT company_id FROM COMPANIES WHERE ticker = %s", (company_data['ticker'],))
            result = cursor.fetchone()
            company_id = result[0] if result else None
            cursor.close()
            
            logger.info(f"Inserted company: {company_data['name']} (ID: {company_id})")
            return company_id
            
        except Exception as e:
            logger.error(f"Failed to insert company {company_data['name']}: {e}")
            return None
    
    def insert_news_article(self, article: NewsArticle) -> Optional[int]:
        """Insert a news article into the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO NEWS_ARTICLES 
            (company_id, title, content, url, source, published_date, scraped_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                article.company_id,
                article.title,
                article.content,
                article.url,
                article.source,
                article.published_date,
                article.scraped_date
            ))
            # Fetch the article_id by url (unique)
            cursor.execute("SELECT article_id FROM NEWS_ARTICLES WHERE url = %s", (article.url,))
            result = cursor.fetchone()
            article_id = result[0] if result else None
            cursor.close()
            
            logger.debug(f"Inserted article: {article.title[:50]}... (ID: {article_id})")
            return article_id
            
        except Exception as e:
            logger.error(f"Failed to insert article: {e}")
            return None
    
    def insert_sentiment_analysis(self, sentiment: SentimentAnalysis) -> Optional[int]:
        """Insert sentiment analysis result into the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO SENTIMENT_ANALYSIS 
            (article_id, company_id, engine, sentiment_score, sentiment_label, 
             confidence_score, keywords)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            keywords_json = json.dumps(sentiment.keywords) if sentiment.keywords else None
            
            cursor.execute(query, (
                sentiment.article_id,
                sentiment.company_id,
                sentiment.engine.value,
                sentiment.sentiment_score,
                sentiment.sentiment_label.value,
                sentiment.confidence_score,
                keywords_json
            ))
            # Fetch the sentiment_id by article_id, company_id, engine (composite unique)
            cursor.execute("SELECT sentiment_id FROM SENTIMENT_ANALYSIS WHERE article_id = %s AND company_id = %s AND engine = %s", (
                sentiment.article_id,
                sentiment.company_id,
                sentiment.engine.value
            ))
            result = cursor.fetchone()
            sentiment_id = result[0] if result else None
            cursor.close()
            
            logger.debug(f"Inserted sentiment analysis (ID: {sentiment_id})")
            return sentiment_id
            
        except Exception as e:
            logger.error(f"Failed to insert sentiment analysis: {e}")
            return None
    
    def insert_daily_summary(self, summary: DailySentimentSummary) -> Optional[int]:
        """Insert daily sentiment summary into the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO DAILY_SENTIMENT_SUMMARY 
            (company_id, date, avg_sentiment_score, sentiment_label, 
             article_count, positive_count, negative_count, neutral_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                summary.company_id,
                summary.date.date(),
                summary.avg_sentiment_score,
                summary.sentiment_label.value,
                summary.article_count,
                summary.positive_count,
                summary.negative_count,
                summary.neutral_count
            ))
            # Fetch the summary_id by company_id and date (composite unique)
            cursor.execute("SELECT summary_id FROM DAILY_SENTIMENT_SUMMARY WHERE company_id = %s AND date = %s", (
                summary.company_id,
                summary.date.date()
            ))
            result = cursor.fetchone()
            summary_id = result[0] if result else None
            cursor.close()
            
            logger.info(f"Inserted daily summary for {summary.company_name} on {summary.date.date()}")
            return summary_id
            
        except Exception as e:
            logger.error(f"Failed to insert daily summary: {e}")
            return None
    
    def get_company_id(self, ticker: str) -> Optional[int]:
        """Get company ID by ticker symbol"""
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT company_id FROM COMPANIES WHERE ticker = %s"
            cursor.execute(query, (ticker.upper(),))
            
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to get company ID for {ticker}: {e}")
            return None
    
    def get_daily_sentiment_data(self, days: int = 7) -> pd.DataFrame:
        """Get daily sentiment data for the last N days"""
        try:
            query = f"""
            SELECT 
                company_name,
                ticker,
                sector,
                date,
                avg_sentiment_score,
                sentiment_label,
                article_count,
                positive_count,
                negative_count,
                neutral_count
            FROM DAILY_SUMMARY_VIEW
            WHERE date >= DATEADD(day, -{days}, CURRENT_DATE())
            ORDER BY date DESC, avg_sentiment_score DESC
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                columns = ['company_name', 'ticker', 'sector', 'date', 'avg_sentiment_score', 
                          'sentiment_label', 'article_count', 'positive_count', 'negative_count', 'neutral_count']
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Retrieved {len(df)} daily sentiment records")
                return df
            else:
                logger.warning("No daily sentiment data found")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get daily sentiment data: {e}")
            return pd.DataFrame()
    
    def get_top_companies_by_sentiment(self, days: int = 30, limit: int = 10) -> pd.DataFrame:
        """Get top companies by average sentiment"""
        try:
            query = f"""
            SELECT 
                company_name,
                ticker,
                sector,
                AVG(avg_sentiment_score) as avg_sentiment,
                COUNT(*) as days_analyzed,
                SUM(article_count) as total_articles
            FROM DAILY_SUMMARY_VIEW
            WHERE date >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY company_name, ticker, sector
            HAVING COUNT(*) >= 5
            ORDER BY avg_sentiment DESC
            LIMIT {limit}
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                columns = ['company_name', 'ticker', 'sector', 'avg_sentiment', 'days_analyzed', 'total_articles']
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Retrieved top {len(df)} companies by sentiment")
                return df
            else:
                logger.warning("No top companies data found")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get top companies: {e}")
            return pd.DataFrame()
    
    def get_sector_sentiment(self, days: int = 7) -> pd.DataFrame:
        """Get sentiment analysis by sector"""
        try:
            query = f"""
            SELECT 
                sector,
                AVG(avg_sentiment_score) as sector_sentiment,
                COUNT(DISTINCT company_name) as company_count,
                SUM(article_count) as total_articles
            FROM DAILY_SUMMARY_VIEW
            WHERE date >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY sector
            ORDER BY sector_sentiment DESC
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                columns = ['sector', 'sector_sentiment', 'company_count', 'total_articles']
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Retrieved sentiment data for {len(df)} sectors")
                return df
            else:
                logger.warning("No sector sentiment data found")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get sector sentiment: {e}")
            return pd.DataFrame()
    
    def get_article_count_by_source(self, days: int = 7) -> pd.DataFrame:
        """Get article count by news source"""
        try:
            query = f"""
            SELECT 
                source,
                COUNT(*) as article_count,
                COUNT(DISTINCT company_id) as companies_covered
            FROM NEWS_ARTICLES
            WHERE scraped_date >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY source
            ORDER BY article_count DESC
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                columns = ['source', 'article_count', 'companies_covered']
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Retrieved article count for {len(df)} sources")
                return df
            else:
                logger.warning("No article count by source data found")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get article count by source: {e}")
            return pd.DataFrame()
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a custom query and return results as DataFrame"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                # Try to get column names from cursor description
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Executed custom query, returned {len(df)} rows")
                return df
            else:
                logger.warning("No results from custom query")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return pd.DataFrame()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect() 