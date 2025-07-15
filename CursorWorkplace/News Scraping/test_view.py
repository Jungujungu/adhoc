from src.database.snowflake_manager import SnowflakeManager

def test_view():
    db = SnowflakeManager()
    db.connect()
    
    try:
        cursor = db.connection.cursor()
        
        # Check if view exists
        cursor.execute("SELECT COUNT(*) FROM DAILY_SUMMARY_VIEW")
        count = cursor.fetchone()[0]
        print(f"Daily summaries in view: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM DAILY_SUMMARY_VIEW LIMIT 3")
            print("Sample data:")
            for row in cursor.fetchall():
                print(row)
        else:
            print("No data in DAILY_SUMMARY_VIEW")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    test_view() 