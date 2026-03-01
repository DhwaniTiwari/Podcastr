from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Subscription Tracking
    podcasts_used = Column(Integer, default=0)
    monthly_reset_date = Column(DateTime(timezone=True), server_default=func.now())
