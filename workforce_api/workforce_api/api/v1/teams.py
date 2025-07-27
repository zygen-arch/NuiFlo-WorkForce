"""Teams API endpoints."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_serializer

from ...core.database import get_db_dependency
from ...services import TeamService
from ...models import ExpertiseLevel
import structlog

logger = structlog.get_logger()
router = APIRouter()


# Request/Response models
class RoleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expertise: ExpertiseLevel
    llm_model: str = Field(default="gpt-3.5-turbo", max_length=50)
    llm_config: Optional[Dict[str, Any]] = None
    agent_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    monthly_budget: Decimal = Field(..., gt=0, description="Monthly budget in USD")
    roles: List[RoleCreate] = Field(default_factory=list, max_length=10)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    monthly_budget: Optional[Decimal] = Field(None, gt=0)


class TeamExecute(BaseModel):
    inputs: Optional[Dict[str, Any]] = Field(None, description="Execution inputs")


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
    owner_id: int
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
    db: Session = Depends(get_db_dependency)
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
        # TODO: Get actual user from authentication
        # For now, use a dummy user ID
        dummy_user_id = 1
        
        # Convert roles data
        roles_data = [role.model_dump() for role in team_data.roles]
        
        team = TeamService.create_team(
            name=team_data.name,
            owner_id=dummy_user_id,
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
    db: Session = Depends(get_db_dependency)
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
        # TODO: Get actual user from authentication
        filter_user_id = user_id or 1  # Default to dummy user
        
        teams = TeamService.list_user_teams(filter_user_id, db)
        
        return [TeamResponse.model_validate(team) for team in teams]
        
    except Exception as e:
        logger.error("Failed to list teams", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db_dependency)
) -> TeamResponse:
    """
    Get team by ID.
    
    Args:
        team_id: Team ID
        db: Database session
        
    Returns:
        Team information
    """
    try:
        team = TeamService.get_team_with_roles(team_id, db)
        
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
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
    db: Session = Depends(get_db_dependency)
) -> TeamResponse:
    """
    Update team information.
    
    Args:
        team_id: Team ID
        team_data: Team update data
        db: Database session
        
    Returns:
        Updated team information
    """
    try:
        team = TeamService.update_team(
            team_id=team_id,
            name=team_data.name,
            description=team_data.description,
            monthly_budget=team_data.monthly_budget,
            session=db
        )
        
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        return TeamResponse.model_validate(team)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Failed to update team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db_dependency)
):
    """
    Delete a team.
    
    Args:
        team_id: Team ID
        db: Database session
    """
    try:
        deleted = TeamService.delete_team(team_id, db)
        
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Failed to delete team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{team_id}/execute", response_model=ExecutionResponse)
def execute_team(
    team_id: int,
    execution_data: Optional[TeamExecute] = None,
    db: Session = Depends(get_db_dependency)
) -> ExecutionResponse:
    """
    Execute a team using CrewAI.
    
    Args:
        team_id: Team ID to execute
        execution_data: Optional execution parameters
        db: Database session
        
    Returns:
        Execution results and metrics
    """
    try:
        inputs = execution_data.inputs if execution_data else None
        
        result = TeamService.execute_team(
            team_id=team_id,
            inputs=inputs,
            session=db
        )
        
        return ExecutionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Failed to execute team", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Team execution failed")


@router.get("/{team_id}/status")
def get_team_status(
    team_id: int,
    db: Session = Depends(get_db_dependency)
) -> Dict[str, Any]:
    """
    Get detailed team status information.
    
    Args:
        team_id: Team ID
        db: Database session
        
    Returns:
        Team status information
    """
    try:
        team = TeamService.get_team_with_roles(team_id, db)
        
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        
        budget_utilization = 0.0
        if team.monthly_budget > 0:
            budget_utilization = float(team.current_spend / team.monthly_budget * 100)
        
        return {
            "team_id": team.id,
            "name": team.name,
            "status": team.status.value,
            "monthly_budget": float(team.monthly_budget),
            "current_spend": float(team.current_spend),
            "budget_utilization": budget_utilization,
            "last_executed_at": team.last_executed_at.isoformat() if team.last_executed_at else None,
            "role_count": len(team.roles),
            "active_roles": len([r for r in team.roles if r.is_active]),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get team status", team_id=team_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 