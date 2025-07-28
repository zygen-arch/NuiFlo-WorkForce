"""Team model for workforce management."""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from . import Base

class TeamStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    auth_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # NEW: References auth.users
    owner_id = Column(Integer, nullable=True)  # LEGACY: Keep for backward compatibility  
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    monthly_budget = Column(Numeric(10, 2), nullable=False)
    current_spend = Column(Numeric(10, 2), default=0.0)
    status = Column(SQLEnum(TeamStatus), default=TeamStatus.IDLE)
    last_executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships  
    # Note: auth_owner_id references auth.users in Supabase, no SQLAlchemy relationship needed
    roles = relationship("Role", back_populates="team", cascade="all, delete-orphan")
    executions = relationship("TeamExecution", back_populates="team", cascade="all, delete-orphan") 