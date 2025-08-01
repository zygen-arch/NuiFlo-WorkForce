from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"

class SpaceSettings(BaseModel):
    storage: Dict[str, Any] = Field(default_factory=lambda: {
        "type": "local",
        "size_gb": 10,
        "external_providers": []
    })
    quotas: Dict[str, Any] = Field(default_factory=lambda: {
        "monthly_budget": 500.0,
        "execution_limit": 1000,
        "agent_limit": 10
    })
    permissions: Dict[str, Any] = Field(default_factory=lambda: {
        "default_agent_access": ["read", "write"],
        "allow_external_storage": True,
        "allow_cross_space_references": False
    })

class SpaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    settings: Optional[SpaceSettings] = None
    storage_config: Optional[Dict[str, Any]] = None

class SpaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    settings: Optional[SpaceSettings] = None
    storage_config: Optional[Dict[str, Any]] = None

class SpaceResponse(BaseModel):
    id: str
    team_id: int
    name: str
    description: Optional[str] = None
    settings: Dict[str, Any]
    storage_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SpaceListResponse(BaseModel):
    spaces: List[SpaceResponse]
    total: int
    page: int
    size: int

class SpaceBillingResponse(BaseModel):
    space_id: str
    current_month_spend: float
    monthly_budget: float
    usage_percentage: float
    agent_costs: Dict[str, float]
    storage_costs: float
    execution_costs: float
    last_updated: datetime

class SpaceActivityResponse(BaseModel):
    space_id: str
    activities: List[Dict[str, Any]]
    total_activities: int
    last_activity: Optional[datetime] = None

class StorageConfig(BaseModel):
    type: StorageType
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    size_gb: Optional[int] = None 