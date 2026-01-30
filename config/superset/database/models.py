"""
SQLAlchemy models for council-ai consultation database.

These models define the database schema for storing consultation data
that can be visualized in Apache Superset dashboards.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Consultation(Base):
    """Model for consultation results."""

    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(String(255), nullable=False, unique=True, index=True)
    query = Column(Text, nullable=False)
    context = Column(Text)
    mode = Column(String(50), nullable=False, index=True)  # synthesis, debate, vote, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Results
    synthesis = Column(Text)
    synthesis_length = Column(Integer)  # Character count

    # Metadata
    tags = Column(JSON)  # List of strings
    notes = Column(Text)
    metadata = Column(JSON)

    # Statistics
    response_count = Column(Integer, default=0)
    total_tokens = Column(Integer)  # If available

    # Indexes for common queries
    __table_args__ = (
        Index("idx_consultation_timestamp", "timestamp"),
        Index("idx_consultation_mode", "mode"),
        Index("idx_consultation_query", "query"),
    )

    def __repr__(self):
        """Representation of the consultation."""
        return f"<Consultation(id={self.consultation_id}, mode={self.mode}, query={self.query[:50]}...)>"


class MemberResponse(Base):
    """Model for individual member responses within a consultation."""

    __tablename__ = "member_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(String(255), nullable=False, index=True)
    member_name = Column(String(255), nullable=False, index=True)
    persona_name = Column(String(255), index=True)
    response_text = Column(Text, nullable=False)
    response_length = Column(Integer)  # Character count

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)

    __table_args__ = (
        Index("idx_response_consultation", "consultation_id", "member_name"),
        Index("idx_response_member", "member_name"),
        Index("idx_response_persona", "persona_name"),
    )

    def __repr__(self):
        """Representation of the member response."""
        return f"<MemberResponse(member={self.member_name}, consultation={self.consultation_id})>"


class ConsultationStats(Base):
    """Aggregated statistics for consultations."""

    __tablename__ = "consultation_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    mode = Column(String(50), nullable=False, index=True)

    # Counts
    total_consultations = Column(Integer, default=0)
    total_responses = Column(Integer, default=0)
    unique_members = Column(Integer, default=0)

    # Averages
    avg_response_length = Column(Float)
    avg_synthesis_length = Column(Float)

    __table_args__ = (Index("idx_stats_date_mode", "date", "mode"),)

    def __repr__(self):
        """Representation of the stats."""
        return f"<ConsultationStats(date={self.date}, mode={self.mode}, count={self.total_consultations})>"
