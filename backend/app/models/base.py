"""SQLAlchemy models for MySQL."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship

from ..config import config

engine = create_engine(
    config.DATABASE_URL.replace("+aiomysql", "+pymysql"),
    echo=False,
    pool_pre_ping=True,
)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    genre = Column(String(50), nullable=False)
    sub_genre = Column(String(50), default="")
    platform = Column(String(50), default="")
    total_episodes = Column(Integer, default=100)
    episode_duration_min = Column(Integer, default=1)
    episode_duration_max = Column(Integer, default=3)
    local_path = Column(String(500), nullable=False, comment="Path to project directory")
    phase = Column(String(20), default="init")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    episodes = relationship("Episode", back_populates="project")
    assets = relationship("Asset", back_populates="project")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200), default="")
    emotion_tone = Column(String(100), default="")
    scenes_count = Column(Integer, default=0)
    shots_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft | reviewed | final
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="episodes")
    assets = relationship("Asset", back_populates="episode")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    asset_type = Column(String(20), nullable=False)  # character_image | scene_image | video
    name = Column(String(200), nullable=False)
    file_path = Column(String(500), default="")
    external_url = Column(String(1000), default="")
    provider = Column(String(50), default="")
    prompt_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="assets")
    episode = relationship("Episode", back_populates="assets")


def init_db():
    Base.metadata.create_all(engine)
