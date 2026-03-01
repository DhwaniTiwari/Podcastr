import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('podcastr.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, audio_path, user_id FROM podcasts ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        
        for row in rows:
            # row: (id, title, audio_path, user_id)
            print(f"ID: {row[0]} -> Path: {row[2]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db()
