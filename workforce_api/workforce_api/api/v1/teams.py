"""Teams API endpoints."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import html
import re

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_serializer, field_validator

from ...core.database import get_db_dependency
from ...core.auth import get_current_user
from ...services import TeamService
from ...models import ExpertiseLevel
import structlog

logger = structlog.get_logger()
router = APIRouter()


def sanitize_string(value: str) -> str:
    """Sanitize string input to prevent XSS attacks."""
    if not isinstance(value, str):
        return value
    
    # Remove HTML tags and escape special characters
    value = re.sub(r'<[^>]*>', '', value)  # Remove HTML tags
    value = html.escape(value)  # Escape HTML characters
    value = value.strip()  # Remove leading/trailing whitespace
    
    return value


# Request/Response models
class RoleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expertise: ExpertiseLevel
    llm_model: str = Field(default="gpt-3.5-turbo", max_length=50)
    llm_config: Optional[Dict[str, Any]] = None
    agent_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    
    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @field_validator('llm_model')
    @classmethod
    def validate_llm_model(cls, v):
        # Whitelist allowed LLM models
        allowed_models = [
            'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'
        ]
        if v not in allowed_models:
            raise ValueError(f'LLM model must be one of: {", ".join(allowed_models)}')
        return v


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    monthly_budget: Decimal = Field(..., gt=0, le=10000, description="Monthly budget in USD (max $10,000)")
    roles: List[RoleCreate] = Field(default_factory=list, max_length=10)
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_string(v)
    
    @field_validator('description')
    @classmethod 
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 roles allowed per team')
        return v


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    monthly_budget: Optional[Decimal] = Field(None, gt=0, le=10000)
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v)
        return v


class TeamExecute(BaseModel):
    inputs: Optional[Dict[str, Any]] = Field(None, description="Execution inputs")
    
    @field_validator('inputs')
    @classmethod
    def validate_inputs(cls, v):
        if v is None:
            return v
        
        # Limit input size to prevent abuse
        if len(str(v)) > 10000:
            raise ValueError('Input data too large (max 10,000 characters)')
        
        # Sanitize string values in inputs
        if isinstance(v, dict):
            sanitized = {}
            for key, value in v.items():
                if isinstance(value, str):
                    sanitized[sanitize_string(key)] = sanitize_string(value)
                else:
                    sanitized[sanitize_string(key)] = value
            return sanitized
        
        return v


class RoleResponse(BaseModel):
    id: int
    team_id: int
    title: str
    description: Optional[str]
    expertise: ExpertiseLevel
    llm_model: str
    llm_config: Optional[Dict[str, Any]]
    agent_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat()

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: int
    auth_owner_id: Optional[str] = None  # UUID from Supabase auth
    owner_id: Optional[int] = None  # Legacy field, now nullable
    name: str
    description: Optional[str]
    monthly_budget: Decimal
    current_spend: Decimal
    status: str
    last_executed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []

    @field_serializer('created_at', 'updated_at', 'last_executed_at')
    def serialize_dt(self, dt: Optional[datetime]) -> Optional[str]:
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    result: Optional[str]
    metrics: Dict[str, Any]
    success: bool
    error: Optional[str]
    team_execution_id: Optional[int]


# API endpoints
@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> TeamResponse:
    """
    Create a new team with roles.
    
    Args:
        team_data: Team creation data
        db: Database session
        
    Returns:
        Created team information
    """
    try:
        # Convert roles data
        roles_data = [role.model_dump() for role in team_data.roles]
        
        team = TeamService.create_team(
            name=team_data.name,
            owner_id=current_user,  # current_user is UUID string
            monthly_budget=team_data.monthly_budget,
            description=team_data.description,
            roles_data=roles_data,
            session=db
        )
        
        # Load team with roles for response
        team_with_roles = TeamService.get_team_with_roles(team.id, db)
        
        return TeamResponse.model_validate(team_with_roles)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Failed to create team", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=List[TeamResponse])
def list_teams(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> List[TeamResponse]:
    """
    List teams.
    
    Args:
        user_id: Optional user ID filter
        db: Database session
        
    Returns:
        List of teams
    """
    try:
        filter_user_id = user_id or current_user  # current_user is UUID string
        
        teams = TeamService.list_user_teams(filter_user_id, db)
        
        return [TeamResponse.model_validate(team) for team in teams]
        
    except Exception as e:
        logger.error("Failed to list teams", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> TeamResponse:
    """
    Get team by ID.
    
    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Team data
    """
    try:
        team = TeamService.get_team_by_id(team_id, db)
        
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        # Check ownership
        if team.auth_owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return TeamResponse.model_validate(team)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> TeamResponse:
    """
    Update team information.
    
    Args:
        team_id: Team ID
        team_data: Updated team data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated team information
    """
    try:
        # Get team and check ownership
        team = TeamService.get_team_by_id(team_id, db)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        if team.auth_owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Update team
        updated_team = TeamService.update_team(
            team_id=team_id,
            name=team_data.name,
            description=team_data.description,
            monthly_budget=team_data.monthly_budget,
            session=db
        )
        
        if not updated_team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        return TeamResponse.model_validate(updated_team)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
):
    """
    Delete team.
    
    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user
    """
    try:
        # Get team and check ownership
        team = TeamService.get_team_by_id(team_id, db)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        if team.auth_owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Delete team
        success = TeamService.delete_team(team_id, db)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{team_id}/execute", response_model=ExecutionResponse)
def execute_team(
    team_id: int,
    execution_data: Optional[TeamExecute] = None,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> ExecutionResponse:
    """
    Execute team workflow.
    
    Args:
        team_id: Team ID
        execution_data: Optional execution parameters
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Execution result
    """
    try:
        # Get team and check ownership
        team = TeamService.get_team_by_id(team_id, db)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        if team.auth_owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Execute team workflow
        inputs = execution_data.inputs if execution_data else {}
        
        result = TeamService.execute_team(team_id, inputs, db)
        
        return ExecutionResponse.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{team_id}/status")
def get_team_status(
    team_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get team status and metrics.
    
    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Team status and performance metrics
    """
    try:
        # Get team and check ownership
        team = TeamService.get_team_by_id(team_id, db)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        if team.auth_owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Get team status
        status_data = TeamService.get_team_status(team_id, db)
        
        return status_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get team status", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 