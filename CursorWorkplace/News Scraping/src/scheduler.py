"""
News Sentiment Scheduler
Automated scheduling for news sentiment analysis
"""

import os
import sys
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main import NewsSentimentScraper

# Load environment variables
load_dotenv()

class NewsSentimentScheduler:
    """Scheduler for automated news sentiment analysis"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = BlockingScheduler()
        self.scraper = NewsSentimentScraper()
        
        # Get scheduling configuration from environment
        self.timezone = os.getenv('SCHEDULER_TIMEZONE', 'UTC')
        self.daily_run_time = os.getenv('DAILY_RUN_TIME', '06:00')
        self.weekly_run_day = os.getenv('WEEKLY_RUN_DAY', 'Monday')
    
    def run_scraping_job(self):
        """Run the news sentiment scraping job"""
        print(f"[{datetime.now()}] Starting scheduled news sentiment analysis...")
        
        try:
            success = self.scraper.run_full_pipeline()
            
            if success:
                print(f"[{datetime.now()}] ✅ Scheduled scraping completed successfully!")
                
                # Print statistics
                stats = self.scraper.get_statistics()
                print(f"[{datetime.now()}] Statistics: {stats}")
            else:
                print(f"[{datetime.now()}] ❌ Scheduled scraping failed!")
                
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Scheduled scraping error: {e}")
    
    def setup_daily_job(self):
        """Setup daily scraping job"""
        hour, minute = self.daily_run_time.split(':')
        
        self.scheduler.add_job(
            func=self.run_scraping_job,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id='daily_news_scraping',
            name='Daily News Sentiment Analysis',
            replace_existing=True
        )
        
        print(f"✅ Daily job scheduled for {self.daily_run_time} {self.timezone}")
    
    def setup_weekly_job(self):
        """Setup weekly scraping job"""
        hour, minute = self.daily_run_time.split(':')
        
        self.scheduler.add_job(
            func=self.run_scraping_job,
            trigger=CronTrigger(
                day_of_week=self.weekly_run_day.lower()[:3],
                hour=int(hour),
                minute=int(minute)
            ),
            id='weekly_news_scraping',
            name='Weekly News Sentiment Analysis',
            replace_existing=True
        )
        
        print(f"✅ Weekly job scheduled for {self.weekly_run_day}s at {self.daily_run_time} {self.timezone}")
    
    def setup_hourly_job(self):
        """Setup hourly scraping job (for testing)"""
        self.scheduler.add_job(
            func=self.run_scraping_job,
            trigger=CronTrigger(minute=0),  # Run at the top of every hour
            id='hourly_news_scraping',
            name='Hourly News Sentiment Analysis',
            replace_existing=True
        )
        
        print("✅ Hourly job scheduled (for testing)")
    
    def run_immediately(self):
        """Run scraping job immediately"""
        print("🚀 Running scraping job immediately...")
        self.run_scraping_job()
    
    def start_scheduler(self, run_immediately: bool = False):
        """Start the scheduler"""
        print("=== Fortune 100 News Sentiment Scheduler ===")
        print(f"Timezone: {self.timezone}")
        print(f"Daily run time: {self.daily_run_time}")
        print(f"Weekly run day: {self.weekly_run_day}")
        
        # Setup jobs
        self.setup_daily_job()
        self.setup_weekly_job()
        
        # Optionally setup hourly job for testing
        if os.getenv('ENABLE_HOURLY_JOBS', 'false').lower() == 'true':
            self.setup_hourly_job()
        
        # Run immediately if requested
        if run_immediately:
            self.run_immediately()
        
        print("\n📅 Scheduler started. Press Ctrl+C to stop.")
        print("Next scheduled runs:")
        for job in self.scheduler.get_jobs():
            job_name = getattr(job, "name", str(job.id))
            next_run = getattr(job, "next_run_time", None)
            if next_run:
                print(f"  - {job_name}: {next_run}")
            else:
                print(f"  - {job_name}: No next run scheduled")
        
        try:
            # Start the scheduler
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\n⏹️ Scheduler stopped by user.")
        except Exception as e:
            print(f"\n❌ Scheduler error: {e}")

def main():
    """Main scheduler function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='News Sentiment Scheduler')
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run scraping job immediately'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Enable hourly jobs for testing'
    )
    
    args = parser.parse_args()
    
    # Set environment variable for testing if requested
    if args.test:
        os.environ['ENABLE_HOURLY_JOBS'] = 'true'
    
    # Initialize and start scheduler
    scheduler = NewsSentimentScheduler()
    scheduler.start_scheduler(run_immediately=args.run_now)

if __name__ == "__main__":
    main() 