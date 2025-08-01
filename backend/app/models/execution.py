"""Execution tracking models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship

from . import Base
from .team import TeamStatus


class TeamExecution(Base):
    __tablename__ = "team_executions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    space_id = Column(String(50), nullable=True)  # Will be NOT NULL after migration
    status = Column(String, nullable=False, default=TeamStatus.RUNNING.value)
    result = Column(Text)  # Final crew output
    error_message = Column(Text)
    execution_metadata = Column(JSON)  # Input params, context
    
    # Resource tracking
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 4), default=0)
    duration_seconds = Column(Numeric(10, 2))
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="executions")
    task_executions = relationship("TaskExecution", back_populates="team_execution", cascade="all, delete-orphan")


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    team_execution_id = Column(Integer, ForeignKey("team_executions.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    space_id = Column(String(50), nullable=True)  # Will be NOT NULL after migration
    task_name = Column(String(100), nullable=False)
    task_description = Column(Text)
    status = Column(String, nullable=False, default=TeamStatus.RUNNING.value)
    
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Resource tracking
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 4), default=0)
    duration_seconds = Column(Numeric(10, 2))
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team_execution = relationship("TeamExecution", back_populates="task_executions")
    role = relationship("Role", back_populates="task_executions") 