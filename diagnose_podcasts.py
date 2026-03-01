import sqlite3

def diagnose():
    try:
        conn = sqlite3.connect('podcastr.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, length(script) FROM podcasts ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print("Latest Podcast Scripts:")
        for row in rows:
            print(f"ID: {row[0]} -> Script Length: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    diagnose()
