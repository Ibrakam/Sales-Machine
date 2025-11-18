"""
Модель истории взаимодействий с лидом
"""
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class InteractionAuthor(Enum):
    ADMIN = "admin"
    CLIENT = "client"
    AI = "ai"


class LeadInteraction(Base):
    __tablename__ = "lead_interactions"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    # Для SQLite используем native_enum=False, чтобы хранить как строки
    author_type = Column(
        SqlEnum(InteractionAuthor, native_enum=False, length=20),
        nullable=False
    )
    author_name = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="interactions")

    def __repr__(self):
        return f"<LeadInteraction(id={self.id}, lead_id={self.lead_id}, author='{self.author_type.value}')>"
