"""Team model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
import enum

from . import Base


class TeamStatus(enum.Enum):
    IDLE = "idle"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    monthly_budget = Column(Numeric(10, 2), nullable=False, default=0)
    current_spend = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Enum(TeamStatus), default=TeamStatus.IDLE)
    last_executed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="teams")
    roles = relationship("Role", back_populates="team", cascade="all, delete-orphan")
    executions = relationship("TeamExecution", back_populates="team", cascade="all, delete-orphan") 