from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import uuid

class TeamSpace(Base):
    """Team Space - Virtual boundary for AI agent operations"""
    __tablename__ = "team_spaces"
    
    id = Column(String(50), primary_key=True, default=lambda: f"space_{uuid.uuid4()}")
    team_id = Column(Integer, nullable=False)  # Remove ForeignKey to avoid circular reference
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Space configuration
    settings = Column(JSON, default={
        "storage": {
            "type": "local",
            "size_gb": 10,
            "external_providers": []
        },
        "quotas": {
            "monthly_budget": 500.0,
            "execution_limit": 1000,
            "agent_limit": 10
        },
        "permissions": {
            "default_agent_access": ["read", "write"],
            "allow_external_storage": True,
            "allow_cross_space_references": False
        }
    })
    
    # External storage configuration
    storage_config = Column(JSON, default={})
    
    # Space metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TeamSpace(id={self.id}, name='{self.name}', team_id={self.team_id})>" 