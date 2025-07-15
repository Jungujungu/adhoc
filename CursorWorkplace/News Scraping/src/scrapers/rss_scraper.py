"""
RSS Feed Scraper
Scrapes news from RSS feeds for Fortune 100 companies
"""

import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse
from loguru import logger

from src.models.news_article import NewsArticle
from config.companies import FORTUNE_100_COMPANIES

class RSSScraper:
    """RSS feed scraper for news collection"""
    
    def __init__(self):
        """Initialize RSS scraper"""
        self.rss_feeds = self._get_rss_feeds()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsSentimentScraper/1.0 (Educational Project)'
        })
    
    def _get_rss_feeds(self) -> List[Dict[str, str]]:
        """Get list of RSS feeds to scrape"""
        return [
            # Financial news sources
            {
                'name': 'Reuters Business',
                'url': 'https://feeds.reuters.com/reuters/businessNews',
                'category': 'business'
            },
            {
                'name': 'Reuters Technology',
                'url': 'https://feeds.reuters.com/reuters/technologyNews',
                'category': 'technology'
            },
            {
                'name': 'Reuters Markets',
                'url': 'https://feeds.reuters.com/reuters/marketsNews',
                'category': 'markets'
            },
            {
                'name': 'Yahoo Finance',
                'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'category': 'finance'
            },
            {
                'name': 'MarketWatch',
                'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
                'category': 'markets'
            },
            {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'category': 'business'
            },
            {
                'name': 'Bloomberg',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'category': 'markets'
            },
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com/feed/',
                'category': 'technology'
            },
            {
                'name': 'Ars Technica',
                'url': 'https://feeds.arstechnica.com/arstechnica/index',
                'category': 'technology'
            },
            {
                'name': 'The Verge',
                'url': 'https://www.theverge.com/rss/index.xml',
                'category': 'technology'
            }
        ]
    
    def _is_recent_article(self, published_date: datetime, days_threshold: int = 7) -> bool:
        """Check if article is recent enough to include"""
        if not published_date:
            return True  # Include articles without date
        
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        return published_date >= threshold_date
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats from RSS feeds"""
        if not date_str:
            return None
        
        # Common date formats in RSS feeds
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
            '%a, %d %b %Y %H:%M:%S %Z',  # RFC 822 with timezone name
            '%Y-%m-%dT%H:%M:%SZ',        # ISO 8601
            '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601 with timezone
            '%Y-%m-%d %H:%M:%S',         # Simple format
            '%d %b %Y %H:%M:%S',         # Another common format
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"
    
    def _is_company_related(self, title: str, content: str, company_search_terms: List[str]) -> bool:
        """Check if article is related to a specific company"""
        if not title:
            return False
        
        # Combine title and content for search
        search_text = title.lower()
        if content:
            search_text += " " + content.lower()
        
        # Check if any company search terms appear in the text
        for term in company_search_terms:
            if term.lower() in search_text:
                return True
        
        return False
    
    def scrape_feed(self, feed_url: str, feed_name: str) -> List[NewsArticle]:
        """Scrape a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"Scraping RSS feed: {feed_name}")
            
            # Parse the RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {feed_name}: {feed.bozo_exception}")
            
            for entry in feed.entries:
                try:
                    # Extract article data
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    
                    # Get content (prefer summary, fallback to content)
                    content = entry.get('summary', '')
                    if not content and hasattr(entry, 'content'):
                        content = entry.content[0].value if entry.content else ''
                    
                    # Get URL
                    url = entry.get('link', '')
                    
                    # Parse published date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        published_date = self._parse_date(entry.published)
                    
                    # Check if article is recent
                    if not self._is_recent_article(published_date):
                        continue
                    
                    # Create article object
                    article = NewsArticle(
                        title=title,
                        content=content,
                        url=url,
                        source=feed_name,
                        published_date=published_date,
                        scraped_date=datetime.utcnow()
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from {feed_name}")
            
        except Exception as e:
            logger.error(f"Failed to scrape RSS feed {feed_name}: {e}")
        
        return articles
    
    def scrape_all_feeds(self) -> List[NewsArticle]:
        """Scrape all RSS feeds"""
        all_articles = []
        
        for feed in self.rss_feeds:
            articles = self.scrape_feed(feed['url'], feed['name'])
            all_articles.extend(articles)
            
            # Add delay between feeds to be respectful
            time.sleep(1)
        
        logger.info(f"Total articles scraped from RSS feeds: {len(all_articles)}")
        return all_articles
    
    def match_articles_to_companies(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Match articles to Fortune 100 companies"""
        matched_articles = []
        
        for article in articles:
            # Check each company's search terms
            for company in FORTUNE_100_COMPANIES:
                if self._is_company_related(
                    article.title, 
                    article.content, 
                    company['search_terms']
                ):
                    # Create a copy of the article with company info
                    article.company_id = company['rank']  # Use rank as temporary ID
                    article.company_name = company['name']
                    article.ticker = company['ticker']
                    matched_articles.append(article)
                    break  # Match to first company found
        
        logger.info(f"Matched {len(matched_articles)} articles to companies")
        return matched_articles
    
    def scrape_and_match(self) -> List[NewsArticle]:
        """Scrape RSS feeds and match articles to companies"""
        logger.info("Starting RSS feed scraping...")
        
        # Scrape all feeds
        articles = self.scrape_all_feeds()
        
        # Match articles to companies
        matched_articles = self.match_articles_to_companies(articles)
        
        logger.info(f"RSS scraping completed. Found {len(matched_articles)} relevant articles")
        return matched_articles
    
    def get_feed_statistics(self) -> Dict[str, Any]:
        """Get statistics about RSS feeds"""
        stats = {
            'total_feeds': len(self.rss_feeds),
            'feed_categories': {},
            'feed_names': []
        }
        
        for feed in self.rss_feeds:
            category = feed['category']
            stats['feed_categories'][category] = stats['feed_categories'].get(category, 0) + 1
            stats['feed_names'].append(feed['name'])
        
        return stats 