from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Float
from sqlalchemy.sql import func
from .db import Base


class Headline(Base):
    __tablename__ = "headlines"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)

    sentiment = Column(String(32), nullable=True, index=True)
    commentary = Column(Text, nullable=True)
    model_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_headlines_published_source", "published_at", "source"),
    )


