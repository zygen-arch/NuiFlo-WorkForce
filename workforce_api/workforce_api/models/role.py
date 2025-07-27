"""Role model for agent configurations."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from . import Base


class ExpertiseLevel(enum.Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    expertise = Column(Enum(ExpertiseLevel), nullable=False)
    llm_model = Column(String(50), nullable=False, default="gpt-3.5-turbo")
    llm_config = Column(JSON)  # Model params (temperature, max_tokens, etc)
    agent_config = Column(JSON)  # CrewAI agent config (tools, backstory, etc)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="roles")
    task_executions = relationship("TaskExecution", back_populates="role") 