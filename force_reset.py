import sqlite3
import os
import shutil

DB_PATH = "podcastr.db"
UPLOAD_DIR = "static/uploads"

def force_reset():
    print("WARNING: forcing raw system reset...")
    
    # 1. Database Reset
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete data
        cursor.execute("DELETE FROM playlists")
        cursor.execute("DELETE FROM podcasts")
        
        # Reset limits
        cursor.execute("UPDATE users SET podcasts_used = 0")
        
        conn.commit()
        print(f"AVAILABLE: Tables cleared and limits reset in {DB_PATH}")
        conn.close()
    except Exception as e:
        print(f"DB ERROR: {e}")

    # 2. File Reset
    try:
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename == ".gitkeep": continue
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"FILE ERROR: Could not delete {filename}: {e}")
        print(f"AVAILABLE: Upload directory {UPLOAD_DIR} cleaned.")
    except Exception as e:
        print(f"DIR ERROR: {e}")

if __name__ == "__main__":
    force_reset()
