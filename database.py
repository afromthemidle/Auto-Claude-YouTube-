"""
Gestión de base de datos SQLite para el podcast automatizado.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = "sqlite:///podcast.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    episode_number = Column(Integer, unique=True, nullable=False)
    character_name = Column(String(200), nullable=False)
    character_nationality = Column(String(100))
    character_profession = Column(String(200))
    script = Column(Text)
    audio_path = Column(String(500))
    video_path = Column(String(500))
    thumbnail_path = Column(String(500))
    youtube_video_id = Column(String(50))
    youtube_url = Column(String(200))
    status = Column(String(50), default="pending")  # pending, generating, uploading, published, error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)


class UsedCharacter(Base):
    __tablename__ = "used_characters"

    id = Column(Integer, primary_key=True, index=True)
    character_name = Column(String(200), unique=True, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def get_used_characters() -> list[str]:
    with Session(engine) as db:
        chars = db.query(UsedCharacter).all()
        return [c.character_name for c in chars]


def add_used_character(name: str):
    with Session(engine) as db:
        char = UsedCharacter(character_name=name)
        db.add(char)
        db.commit()


def get_next_episode_number() -> int:
    with Session(engine) as db:
        last = db.query(Episode).order_by(Episode.episode_number.desc()).first()
        return (last.episode_number + 1) if last else 1


def create_episode(episode_number: int, character_name: str, nationality: str = None, profession: str = None) -> Episode:
    with Session(engine) as db:
        ep = Episode(
            episode_number=episode_number,
            character_name=character_name,
            character_nationality=nationality,
            character_profession=profession,
            status="pending",
        )
        db.add(ep)
        db.commit()
        db.refresh(ep)
        return ep


def update_episode(episode_id: int, **kwargs):
    with Session(engine) as db:
        ep = db.query(Episode).filter(Episode.id == episode_id).first()
        if ep:
            for key, value in kwargs.items():
                setattr(ep, key, value)
            db.commit()


def get_all_episodes() -> list[Episode]:
    with Session(engine) as db:
        return db.query(Episode).order_by(Episode.episode_number.desc()).all()


def get_episode(episode_id: int) -> Episode | None:
    with Session(engine) as db:
        return db.query(Episode).filter(Episode.id == episode_id).first()
