"""
Test Scraper
Simple test script to verify the scraper components work
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_rss_scraper():
    """Test RSS scraper functionality"""
    print("Testing RSS Scraper...")
    
    try:
        from scrapers.rss_scraper import RSSScraper
        
        scraper = RSSScraper()
        
        # Test feed statistics
        stats = scraper.get_feed_statistics()
        print(f"✅ RSS Scraper initialized successfully")
        print(f"   - Total feeds: {stats['total_feeds']}")
        print(f"   - Categories: {list(stats['feed_categories'].keys())}")
        
        # Test scraping (limited to first feed for testing)
        print("\nTesting RSS feed scraping...")
        if scraper.rss_feeds:
            test_feed = scraper.rss_feeds[0]
            articles = scraper.scrape_feed(test_feed['url'], test_feed['name'])
            print(f"✅ Scraped {len(articles)} articles from {test_feed['name']}")
            
            if articles:
                print(f"   - Sample article: {articles[0].title[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RSS Scraper test failed: {e}")
        return False

def test_sentiment_analyzer():
    """Test sentiment analyzer functionality"""
    print("\nTesting Sentiment Analyzer...")
    
    try:
        from sentiment.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        # Test text analysis
        test_text = "Apple reported strong quarterly earnings, exceeding analyst expectations."
        analyses = analyzer.analyze_text(test_text)
        
        print(f"✅ Sentiment Analyzer initialized successfully")
        print(f"   - Analyzed text with {len(analyses)} engines")
        
        for analysis in analyses:
            print(f"   - {analysis.engine.value}: {analysis.sentiment_label.value} ({analysis.sentiment_score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment Analyzer test failed: {e}")
        return False

def test_models():
    """Test data models"""
    print("\nTesting Data Models...")
    
    try:
        from models.news_article import NewsArticle, SentimentAnalysis, SentimentEngine, SentimentLabel
        
        # Test NewsArticle model
        article = NewsArticle(
            title="Test Article",
            content="This is a test article for sentiment analysis.",
            source="Test Source",
            url="https://example.com/test"
        )
        
        print(f"✅ NewsArticle model works")
        print(f"   - Title: {article.title}")
        print(f"   - Source: {article.source}")
        
        # Test SentimentAnalysis model
        sentiment = SentimentAnalysis(
            engine=SentimentEngine.TEXTBLOB,
            sentiment_score=0.5,
            sentiment_label=SentimentLabel.POSITIVE,
            confidence_score=0.8
        )
        
        print(f"✅ SentimentAnalysis model works")
        print(f"   - Engine: {sentiment.engine.value}")
        print(f"   - Label: {sentiment.sentiment_label.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Models test failed: {e}")
        return False

def test_companies_config():
    """Test companies configuration"""
    print("\nTesting Companies Configuration...")
    
    try:
        from config.companies import FORTUNE_100_COMPANIES, get_company_by_ticker, get_all_tickers
        
        print(f"✅ Companies configuration loaded")
        print(f"   - Total companies: {len(FORTUNE_100_COMPANIES)}")
        
        # Test company lookup
        apple = get_company_by_ticker("AAPL")
        if apple:
            print(f"   - Found Apple: {apple['name']} ({apple['ticker']})")
        
        # Test ticker list
        tickers = get_all_tickers()
        print(f"   - Sample tickers: {tickers[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Companies Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Fortune 100 News Sentiment Scraper Tests ===")
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        test_companies_config,
        test_models,
        test_sentiment_analyzer,
        test_rss_scraper
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! The scraper components are working correctly.")
        print("\nNext steps:")
        print("1. Set up your Snowflake credentials in .env file")
        print("2. Run: python scripts/setup_database.py")
        print("3. Run: python src/main.py")
        print("4. Start dashboard: streamlit run src/dashboard.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 