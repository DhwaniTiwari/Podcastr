from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

SQL_ALCHEMY_DATABASE_URL = settings.DATABASE_URL

if "sqlite" in SQL_ALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQL_ALCHEMY_DATABASE_URL,
        pool_pre_ping=True,    # Test connection before use — fixes Neon SSL drop errors
        pool_recycle=300,      # Recycle connections every 5 minutes
        pool_size=5,
        max_overflow=2
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
