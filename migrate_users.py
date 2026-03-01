import sqlite3
import datetime

conn = sqlite3.connect('podcastr.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN podcasts_used INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE users ADD COLUMN monthly_reset_date TIMESTAMP")
    
    # Set default reset date to today for existing users
    now = datetime.datetime.now().isoformat()
    cursor.execute(f"UPDATE users SET monthly_reset_date = '{now}'")
    
    print("Columns added successfully.")
except Exception as e:
    print(f"Error (probably already exists): {e}")

conn.commit()
conn.close()
