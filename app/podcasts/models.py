from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association Table for Many-to-Many relationship between Playlist and Podcast
playlist_podcast_association = Table(
    'playlist_podcast', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id', ondelete="CASCADE")),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', ondelete="CASCADE"))
)

class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    voice = Column(String, nullable=False)
    script = Column(Text, nullable=False)
    audio_path = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    views = Column(Integer, default=0)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="podcasts")
    playlists = relationship("Playlist", secondary=playlist_podcast_association, back_populates="podcasts")

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="playlists")
    podcasts = relationship("Podcast", secondary=playlist_podcast_association, back_populates="playlists")
