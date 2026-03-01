from app.database import SessionLocal
from app.podcasts.models import Podcast

def check_podcasts():
    db = SessionLocal()
    try:
        podcasts = db.query(Podcast).order_by(Podcast.created_at.desc()).limit(5).all()
        print(f"{'ID':<5} | {'Title':<40} | {'Audio Path':<50} | {'User ID'}")
        print("-" * 110)
        for p in podcasts:
            print(f"{p.id:<5} | {p.title[:37]+'...':<40} | {p.audio_path:<50} | {p.user_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_podcasts()
