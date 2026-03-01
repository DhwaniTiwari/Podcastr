from app.database import SessionLocal
from app.podcasts.models import Podcast, Playlist
from app.auth.models import User
import os
import shutil

def reset_all():
    db = SessionLocal()
    try:
        print("Starting System Reset...")
        
        # 1. Delete all Playlists
        deleted_playlists = db.query(Playlist).delete()
        print(f"Deleted {deleted_playlists} playlists.")
        
        # 2. Delete all Podcasts
        deleted_podcasts = db.query(Podcast).delete()
        print(f"Deleted {deleted_podcasts} podcasts.")
        
        # 3. Reset User Limits
        users = db.query(User).all()
        for user in users:
            user.podcasts_used = 0
            db.add(user)
        print(f"Reset usage limits for {len(users)} users.")
        
        db.commit()
        
        # 4. Clean static/uploads
        upload_dir = "static/uploads"
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename == ".gitkeep": continue
                file_path = os.path.join(upload_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        print("Cleaned static/uploads directory.")
        
        print("System Reset Complete! 🚀")
        
    except Exception as e:
        print(f"Error during reset: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_all()
