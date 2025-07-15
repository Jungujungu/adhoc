"""
Database Setup Script
Initializes Snowflake database tables and views
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.snowflake_manager import SnowflakeManager
from config.companies import FORTUNE_100_COMPANIES

# Load environment variables
load_dotenv()

def setup_database():
    """Setup Snowflake database"""
    print("Setting up Snowflake database...")
    
    try:
        # Initialize database manager
        db_manager = SnowflakeManager()
        
        # Connect to Snowflake
        if not db_manager.connect():
            print("Failed to connect to Snowflake. Please check your configuration.")
            return False
        
        # Setup database tables and views
        print("Creating database tables and views...")
        success = db_manager.setup_database()
        
        if success:
            print("Database setup completed successfully!")
            
            # Populate companies table
            print("Populating companies table...")
            for company in FORTUNE_100_COMPANIES:
                company_id = db_manager.insert_company(company)
                if company_id:
                    print(f"Added company: {company['name']} (ID: {company_id})")
                else:
                    print(f"Failed to add company: {company['name']}")
            
            print("Database setup and population completed!")
            return True
        else:
            print("Database setup failed!")
            return False
            
    except Exception as e:
        print(f"Database setup error: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()

def main():
    """Main setup function"""
    print("=== Fortune 100 News Sentiment Database Setup ===")
    
    success = setup_database()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("You can now run the main scraper with: python src/main.py")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your Snowflake configuration and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 