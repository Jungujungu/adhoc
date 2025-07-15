"""
Main News Sentiment Scraper
Orchestrates the entire news sentiment analysis process
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.rss_scraper import RSSScraper
from src.sentiment.sentiment_analyzer import SentimentAnalyzer
from src.database.snowflake_manager import SnowflakeManager
from src.models.news_article import (
    NewsArticle, 
    SentimentAnalysis, 
    NewsArticleWithSentiment,
    DailySentimentSummary,
    SentimentLabel
)
from config.companies import FORTUNE_100_COMPANIES

# Load environment variables
load_dotenv()

class NewsSentimentScraper:
    """Main orchestrator for news sentiment analysis"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.rss_scraper = RSSScraper()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.db_manager = SnowflakeManager()
        
        # Setup logging
        logger.add(
            "logs/scraper.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    def setup_database(self) -> bool:
        """Setup Snowflake database"""
        try:
            logger.info("Setting up database...")
            success = self.db_manager.setup_database()
            if success:
                logger.info("Database setup completed successfully")
            else:
                logger.error("Database setup failed")
            return success
        except Exception as e:
            logger.error(f"Database setup error: {e}")
            return False
    
    def populate_companies(self) -> bool:
        """Populate companies table with Fortune 100 data"""
        try:
            logger.info("Populating companies table...")
            
            with self.db_manager:
                for company in FORTUNE_100_COMPANIES:
                    # Check if company already exists
                    existing_id = self.db_manager.get_company_id(company['ticker'])
                    if not existing_id:
                        company_id = self.db_manager.insert_company(company)
                        if company_id:
                            logger.info(f"Added company: {company['name']} (ID: {company_id})")
                        else:
                            logger.warning(f"Failed to add company: {company['name']}")
                    else:
                        logger.debug(f"Company already exists: {company['name']} (ID: {existing_id})")
            
            logger.info("Companies population completed")
            return True
            
        except Exception as e:
            logger.error(f"Companies population error: {e}")
            return False
    
    def scrape_news(self) -> List[NewsArticle]:
        """Scrape news articles"""
        try:
            logger.info("Starting news scraping...")
            
            # Scrape RSS feeds
            articles = self.rss_scraper.scrape_and_match()
            
            logger.info(f"Scraped {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"News scraping error: {e}")
            return []
    
    def analyze_sentiment(self, articles: List[NewsArticle]) -> List[NewsArticleWithSentiment]:
        """Analyze sentiment for articles"""
        try:
            logger.info("Starting sentiment analysis...")
            
            articles_with_sentiment = []
            
            for i, article in enumerate(articles):
                try:
                    # Analyze sentiment
                    sentiment_analyses = self.sentiment_analyzer.analyze_article(
                        title=article.title,
                        content=article.content
                    )
                    
                    if sentiment_analyses:
                        # Create combined object
                        article_with_sentiment = NewsArticleWithSentiment(
                            article=article,
                            sentiment_analyses=sentiment_analyses
                        )
                        articles_with_sentiment.append(article_with_sentiment)
                        
                        logger.debug(f"Analyzed article {i+1}/{len(articles)}: {article.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Sentiment analysis failed for article: {e}")
                    continue
            
            logger.info(f"Completed sentiment analysis for {len(articles_with_sentiment)} articles")
            return articles_with_sentiment
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return []
    
    def store_data(self, articles_with_sentiment: List[NewsArticleWithSentiment]) -> bool:
        """Store articles and sentiment data in Snowflake"""
        try:
            logger.info("Storing data in Snowflake...")
            
            with self.db_manager:
                stored_count = 0
                
                for article_with_sentiment in articles_with_sentiment:
                    try:
                        article = article_with_sentiment.article
                        sentiment_analyses = article_with_sentiment.sentiment_analyses
                        
                        # Get company ID
                        company_id = self.db_manager.get_company_id(article.ticker)
                        if not company_id:
                            logger.warning(f"Company not found: {article.ticker}")
                            continue
                        
                        # Update article with company ID
                        article.company_id = company_id
                        
                        # Insert article
                        article_id = self.db_manager.insert_news_article(article)
                        if not article_id:
                            continue
                        
                        # Insert sentiment analyses
                        for sentiment_analysis in sentiment_analyses:
                            sentiment_analysis.article_id = article_id
                            sentiment_analysis.company_id = company_id
                            
                            sentiment_id = self.db_manager.insert_sentiment_analysis(sentiment_analysis)
                            if sentiment_id:
                                stored_count += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to store article: {e}")
                        continue
                
                logger.info(f"Stored {stored_count} sentiment analyses")
                return stored_count > 0
                
        except Exception as e:
            logger.error(f"Data storage error: {e}")
            return False
    
    def generate_daily_summaries(self) -> bool:
        """Generate daily sentiment summaries"""
        try:
            logger.info("Generating daily summaries...")
            
            with self.db_manager:
                # Get today's date
                today = datetime.now().date()
                
                # Query to get daily summaries
                query = """
                SELECT 
                    c.company_id,
                    c.name as company_name,
                    c.ticker,
                    DATE(sa.created_at) as date,
                    AVG(sa.sentiment_score) as avg_sentiment_score,
                    COUNT(DISTINCT sa.article_id) as article_count,
                    SUM(CASE WHEN sa.sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN sa.sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count,
                    SUM(CASE WHEN sa.sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neutral_count
                FROM SENTIMENT_ANALYSIS sa
                JOIN COMPANIES c ON sa.company_id = c.company_id
                WHERE DATE(sa.created_at) = %s
                GROUP BY c.company_id, c.name, c.ticker, DATE(sa.created_at)
                """
                
                cursor = self.db_manager.connection.cursor()
                cursor.execute(query, (today,))
                results = cursor.fetchall()
                cursor.close()
                
                summaries_created = 0
                
                for result in results:
                    try:
                        (company_id, company_name, ticker, date, avg_score, 
                         article_count, positive_count, negative_count, neutral_count) = result
                        
                        # Determine sentiment label
                        if avg_score > 0.1:
                            sentiment_label = SentimentLabel.POSITIVE
                        elif avg_score < -0.1:
                            sentiment_label = SentimentLabel.NEGATIVE
                        else:
                            sentiment_label = SentimentLabel.NEUTRAL
                        
                        # Create summary
                        summary = DailySentimentSummary(
                            company_id=company_id,
                            company_name=company_name,
                            ticker=ticker,
                            date=datetime.combine(date, datetime.min.time()),
                            avg_sentiment_score=float(avg_score),
                            sentiment_label=sentiment_label,
                            article_count=article_count,
                            positive_count=positive_count,
                            negative_count=negative_count,
                            neutral_count=neutral_count
                        )
                        
                        # Insert summary
                        summary_id = self.db_manager.insert_daily_summary(summary)
                        if summary_id:
                            summaries_created += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to create summary for {company_name}: {e}")
                        continue
                
                logger.info(f"Created {summaries_created} daily summaries")
                return summaries_created > 0
                
        except Exception as e:
            logger.error(f"Daily summary generation error: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """Run the complete news sentiment analysis pipeline"""
        try:
            logger.info("Starting full news sentiment analysis pipeline...")
            
            # Step 1: Setup database
            if not self.setup_database():
                logger.error("Database setup failed")
                return False
            
            # Step 2: Populate companies
            if not self.populate_companies():
                logger.error("Companies population failed")
                return False
            
            # Step 3: Scrape news
            articles = self.scrape_news()
            if not articles:
                logger.warning("No articles scraped")
                return False
            
            # Step 4: Analyze sentiment
            articles_with_sentiment = self.analyze_sentiment(articles)
            if not articles_with_sentiment:
                logger.warning("No sentiment analysis completed")
                return False
            
            # Step 5: Store data
            if not self.store_data(articles_with_sentiment):
                logger.error("Data storage failed")
                return False
            
            # Step 6: Generate daily summaries
            if not self.generate_daily_summaries():
                logger.warning("Daily summary generation failed")
            
            logger.info("Pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        try:
            with self.db_manager:
                stats = {
                    'total_companies': len(FORTUNE_100_COMPANIES),
                    'rss_feeds': self.rss_scraper.get_feed_statistics(),
                    'database_stats': {}
                }
                
                # Get database statistics
                cursor = self.db_manager.connection.cursor()
                
                # Article count
                cursor.execute("SELECT COUNT(*) FROM NEWS_ARTICLES")
                stats['database_stats']['total_articles'] = cursor.fetchone()[0]
                
                # Sentiment analysis count
                cursor.execute("SELECT COUNT(*) FROM SENTIMENT_ANALYSIS")
                stats['database_stats']['total_sentiment_analyses'] = cursor.fetchone()[0]
                
                # Daily summaries count
                cursor.execute("SELECT COUNT(*) FROM DAILY_SENTIMENT_SUMMARY")
                stats['database_stats']['total_daily_summaries'] = cursor.fetchone()[0]
                
                cursor.close()
                
                return stats
                
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {}

def main():
    """Main entry point"""
    try:
        # Initialize scraper
        scraper = NewsSentimentScraper()
        
        # Run pipeline
        success = scraper.run_full_pipeline()
        
        if success:
            logger.info("News sentiment analysis completed successfully!")
            
            # Print statistics
            stats = scraper.get_statistics()
            logger.info(f"Statistics: {stats}")
        else:
            logger.error("News sentiment analysis failed!")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 