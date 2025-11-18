"""
Модель подключения Instagram
"""
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.core.database import Base


class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False)
    business_account_id = Column(String(255), nullable=True)
    profile_url = Column(String(500), nullable=True)
    followers_count = Column(Integer, nullable=True)

    access_token = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, connected, disconnected
    connected_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    integration_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<InstagramAccount(id={self.id}, username='{self.username}', status='{self.status}')>"
