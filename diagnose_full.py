import sqlite3
import os

def diagnose_full():
    try:
        conn = sqlite3.connect('podcastr.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, audio_path FROM podcasts ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print(f"{'ID':<5} | {'Audio Path in DB':<60} | {'File Status'}")
        print("-" * 100)
        
        for row in rows:
            pid, title, db_path = row
            
            # DB Path usually starts with /static/...
            # We need to convert it to a local file system path
            if db_path:
                local_path = db_path.lstrip("/") # Remove leading slash
                local_path = local_path.replace("/", os.sep) # Fix separators for Windows
                
                exists = os.path.exists(local_path)
                status = "MISSING"
                if exists:
                    size = os.path.getsize(local_path)
                    status = f"OK ({size} bytes)" if size > 100 else f"CORRUPT ({size} bytes)"
            else:
                status = "NO PATH"
                db_path = "NULL"

            print(f"{pid:<5} | {db_path:<60} | {status}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    diagnose_full()
