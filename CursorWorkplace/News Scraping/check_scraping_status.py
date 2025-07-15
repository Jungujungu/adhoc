#!/usr/bin/env python3
"""
Check Scraping Status
Script to verify if today's daily scraping ran successfully
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_logs():
    """Check recent log entries for today's scraping"""
    print("📋 Checking log files...")
    
    log_file = Path("logs/scraper.log")
    if not log_file.exists():
        print("❌ No log file found at logs/scraper.log")
        return False
    
    # Read the last 50 lines of the log
    with open(log_file, 'r') as f:
        lines = f.readlines()
        recent_lines = lines[-50:] if len(lines) > 50 else lines
    
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    # Look for today's successful runs
    successful_runs = []
    failed_runs = []
    
    for line in recent_lines:
        if today_str in line:
            if "Pipeline completed successfully!" in line:
                successful_runs.append(line.strip())
            elif "Pipeline error:" in line or "Failed" in line:
                failed_runs.append(line.strip())
    
    if successful_runs:
        print(f"✅ Found {len(successful_runs)} successful scraping run(s) today")
        for run in successful_runs[-3:]:  # Show last 3 runs
            print(f"   - {run}")
        return True
    elif failed_runs:
        print(f"❌ Found {len(failed_runs)} failed scraping run(s) today")
        for run in failed_runs[-3:]:
            print(f"   - {run}")
        return False
    else:
        print("⚠️ No scraping activity found in today's logs")
        return False

def check_database():
    """Check database for today's data"""
    print("\n🗄️ Checking database for today's data...")
    
    try:
        from src.database.snowflake_manager import SnowflakeManager
        
        with SnowflakeManager() as db_manager:
            if not db_manager.connection:
                print("❌ No database connection available")
                return False
                
            cursor = db_manager.connection.cursor()
            
            # Check for today's articles
            today = date.today()
            cursor.execute("""
                SELECT COUNT(*) FROM NEWS_ARTICLES 
                WHERE DATE(created_at) = %s
            """, (today,))
            result = cursor.fetchone()
            today_articles = result[0] if result else 0
            
            # Check for today's sentiment analyses
            cursor.execute("""
                SELECT COUNT(*) FROM SENTIMENT_ANALYSIS 
                WHERE DATE(created_at) = %s
            """, (today,))
            result = cursor.fetchone()
            today_sentiments = result[0] if result else 0
            
            # Check for today's daily summaries
            cursor.execute("""
                SELECT COUNT(*) FROM DAILY_SENTIMENT_SUMMARY 
                WHERE DATE(date) = %s
            """, (today,))
            result = cursor.fetchone()
            today_summaries = result[0] if result else 0
            
            cursor.close()
            
            print(f"   📰 Articles today: {today_articles}")
            print(f"   🧠 Sentiment analyses today: {today_sentiments}")
            print(f"   📊 Daily summaries today: {today_summaries}")
            
            if today_articles > 0 and today_sentiments > 0:
                print("✅ Database shows today's scraping was successful")
                return True
            else:
                print("❌ No today's data found in database")
                return False
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_scheduler_status():
    """Check if scheduler is running"""
    print("\n⏰ Checking scheduler status...")
    
    try:
        import psutil
        
        # Look for Python processes running the scheduler
        scheduler_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('scheduler.py' in arg for arg in cmdline):
                    scheduler_running = True
                    print(f"✅ Scheduler is running (PID: {proc.info['pid']})")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not scheduler_running:
            print("⚠️ Scheduler process not found")
            print("💡 To start scheduler: python src/scheduler.py")
        
        return scheduler_running
        
    except ImportError:
        print("⚠️ psutil not installed - cannot check scheduler status")
        print("💡 Install with: pip install psutil")
        return None

def check_next_scheduled_run():
    """Check when the next scheduled run is"""
    print("\n📅 Checking next scheduled run...")
    
    try:
        from src.scheduler import NewsSentimentScheduler
        
        scheduler = NewsSentimentScheduler()
        
        # Get the daily job
        jobs = scheduler.scheduler.get_jobs()
        daily_job = None
        
        for job in jobs:
            if job.id == 'daily_news_scraping':
                daily_job = job
                break
        
        if daily_job:
            next_run = daily_job.next_run_time
            if next_run:
                print(f"✅ Next scheduled run: {next_run}")
                return next_run
            else:
                print("⚠️ Daily job found but no next run time")
                return None
        else:
            print("❌ Daily job not found in scheduler")
            return None
            
    except Exception as e:
        print(f"❌ Could not check scheduler: {e}")
        return None

def main():
    """Main function to check scraping status"""
    print("🔍 Fortune 100 News Sentiment Scraping Status Check")
    print("=" * 50)
    
    # Check logs
    logs_ok = check_logs()
    
    # Check database
    db_ok = check_database()
    
    # Check scheduler
    scheduler_ok = check_scheduler_status()
    
    # Check next run
    next_run = check_next_scheduled_run()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if logs_ok and db_ok:
        print("✅ TODAY'S SCRAPING: SUCCESSFUL")
        print("   - Logs show successful completion")
        print("   - Database contains today's data")
    elif logs_ok and not db_ok:
        print("⚠️ TODAY'S SCRAPING: PARTIAL SUCCESS")
        print("   - Logs show completion but database check failed")
    elif not logs_ok and db_ok:
        print("⚠️ TODAY'S SCRAPING: UNCLEAR")
        print("   - Database has data but no recent logs")
    else:
        print("❌ TODAY'S SCRAPING: NOT RUN OR FAILED")
        print("   - No evidence of successful scraping today")
    
    if scheduler_ok:
        print("✅ SCHEDULER: RUNNING")
    elif scheduler_ok is False:
        print("❌ SCHEDULER: NOT RUNNING")
        print("💡 Start with: python src/scheduler.py")
    else:
        print("⚠️ SCHEDULER: STATUS UNKNOWN")
    
    if next_run:
        print(f"📅 NEXT RUN: {next_run}")
    
    print("\n💡 Manual run command: python src/main.py")
    print("💡 Dashboard: streamlit run src/dashboard.py")

if __name__ == "__main__":
    main() 