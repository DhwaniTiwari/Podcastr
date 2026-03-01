import sqlite3
import os

def check_occult():
    try:
        conn = sqlite3.connect('podcastr.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, audio_path FROM podcasts WHERE title LIKE '%Occult%'")
        rows = cursor.fetchall()
        
        print(f"{'ID':<5} | {'Title':<30} | {'Audio Path':<50} | {'File Exists?'}")
        print("-" * 110)
        
        for row in rows:
            pid, title, db_path = row
            status = "NO PATH"
            size = 0
            
            if db_path:
                local_path = db_path.lstrip("/")
                local_path = local_path.replace("/", os.sep)
                if os.path.exists(local_path):
                    size = os.path.getsize(local_path)
                    status = f"YES ({size} B)"
                else:
                    status = "MISSING"
            
            print(f"{pid:<5} | {title[:27]+'...':<30} | {str(db_path):<50} | {status}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_occult()
