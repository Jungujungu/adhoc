#!/usr/bin/env python3
"""
Test script to check Snowflake connection and table access.
"""

import os
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

def test_snowflake_connection():
    """Test Snowflake connection and table access"""
    print("🔍 Testing Snowflake Connection and Table Access")
    print("=" * 50)
    
    try:
        # Get configuration
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        password = os.getenv('SNOWFLAKE_PASSWORD')
        warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        database = os.getenv('SNOWFLAKE_DATABASE')
        schema = os.getenv('SNOWFLAKE_SCHEMA', 'KANGACCOUNTING')
        table = os.getenv('KEYWORD_TABLE', 'JUNG_AMAZON')
        
        print(f"Account: {account}")
        print(f"User: {user}")
        print(f"Database: {database}")
        print(f"Schema: {schema}")
        print(f"Table: {table}")
        print()
        
        # Connect to Snowflake
        print("🔄 Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        print("✅ Connected to Snowflake successfully!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ Snowflake version: {version}")
        
        # Test table existence
        print(f"\n🔄 Checking if table {table} exists...")
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Table {table} found!")
        else:
            print(f"❌ Table {table} not found!")
            print("Available tables in schema:")
            cursor.execute("SHOW TABLES")
            all_tables = cursor.fetchall()
            for t in all_tables:
                print(f"  - {t[1]}")
        
        # Test table schema
        print(f"\n🔄 Getting schema for table {table}...")
        try:
            cursor.execute(f"DESCRIBE TABLE {table}")
            schema_data = cursor.fetchall()
            print(f"✅ Table schema retrieved successfully!")
            print("Columns:")
            for row in schema_data:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'Y' else 'NOT NULL'})")
        except Exception as e:
            print(f"❌ Error getting table schema: {e}")
        
        # Test sample data
        print(f"\n🔄 Testing sample data query...")
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table has {count:,} rows")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                sample_data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                print("Sample data:")
                for row in sample_data:
                    print(f"  {dict(zip(columns, row))}")
        except Exception as e:
            print(f"❌ Error querying sample data: {e}")
        
        cursor.close()
        conn.close()
        print("\n✅ Snowflake test completed successfully!")
        
    except Exception as e:
        print(f"❌ Snowflake test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_snowflake_connection() 