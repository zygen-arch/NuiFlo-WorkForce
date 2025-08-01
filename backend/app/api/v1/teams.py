"""Teams API endpoints."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import html
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_serializer, field_validator

from ...core.database import get_db_dependency
from ...core.auth import get_current_user
from ...services import TeamService
from ...models import ExpertiseLevel
from ...models.role import Role
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
        # Whitelist allowed LLM models including Ollama models
        allowed_models = [
            # OpenAI Models
            'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 
            # Anthropic Models
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
            # Ollama Models (local)
            'deepseek-coder:6.7b', 'deepseek-coder:33b', 'deepseek-coder:1.3b',
            'llama2:7b', 'llama2:13b', 'llama2:70b',
            'mistral:7b', 'mistral:13b',
            'codellama:7b', 'codellama:13b', 'codellama:34b',
            'neural-chat:7b', 'neural-chat:13b',
            # Add more Ollama models as needed
        ]
        if v not in allowed_models:
            raise ValueError(f'LLM model must be one of: {", ".join(allowed_models)}')
        return v


class RoleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expertise: Optional[ExpertiseLevel] = None
    llm_model: Optional[str] = Field(None, max_length=50)
    llm_config: Optional[Dict[str, Any]] = None
    agent_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
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
        if v is None:
            return v
        # Same validation as RoleCreate
        allowed_models = [
            # OpenAI Models
            'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 
            # Anthropic Models
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
            # Ollama Models (local)
            'deepseek-coder:6.7b', 'deepseek-coder:33b', 'deepseek-coder:1.3b',
            'llama2:7b', 'llama2:13b', 'llama2:70b',
            'mistral:7b', 'mistral:13b',
            'codellama:7b', 'codellama:13b', 'codellama:34b',
            'neural-chat:7b', 'neural-chat:13b',
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

    @field_validator('auth_owner_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings."""
        if isinstance(v, UUID):
            return str(v)
        return v

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


@router.get("/{team_id}/execute/{execution_id}/status")
def get_execution_status(
    team_id: int,
    execution_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get real-time status of a team execution for progress updates."""
    try:
        # Verify team ownership
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Find the execution
        from ...models.execution import TeamExecution
        execution = db.query(TeamExecution).filter(
            TeamExecution.id == execution_id,
            TeamExecution.team_id == team_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Calculate progress based on task executions
        total_tasks = len(execution.task_executions) if execution.task_executions else 1
        completed_tasks = len([t for t in execution.task_executions if t.status == "SUCCESS"]) if execution.task_executions else 0
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Get current step/task
        current_task = None
        if execution.task_executions:
            running_tasks = [t for t in execution.task_executions if t.status == "RUNNING"]
            if running_tasks:
                current_task = {
                    "id": running_tasks[0].id,
                    "agent_name": running_tasks[0].role.title if running_tasks[0].role else "Unknown",
                    "description": running_tasks[0].result[:100] + "..." if running_tasks[0].result and len(running_tasks[0].result) > 100 else running_tasks[0].result
                }
        
        return {
            "execution_id": execution.id,
            "team_id": team_id,
            "status": execution.status,
            "progress_percentage": round(progress_percentage, 1),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "current_task": current_task,
            "started_at": execution.created_at.isoformat(),
            "cost_so_far": float(execution.cost) if execution.cost else 0.0,
            "estimated_completion": None,  # Could add time estimation logic
            "logs": [
                {
                    "timestamp": task.created_at.isoformat(),
                    "agent": task.role.title if task.role else "System",
                    "message": task.result[:200] + "..." if task.result and len(task.result) > 200 else task.result or "Task started"
                }
                for task in (execution.task_executions[-5:] if execution.task_executions else [])
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{team_id}/status")
def get_team_status(
    team_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get team execution status and metrics."""
    try:
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get latest execution
        latest_execution = None
        if team.executions:
            latest_execution = max(team.executions, key=lambda x: x.created_at)
        
        return {
            "team_id": team.id,
            "name": team.name,
            "status": team.status.value,
            "current_spend": float(team.current_spend),
            "monthly_budget": float(team.monthly_budget),
            "budget_remaining": float(team.monthly_budget - team.current_spend),
            "last_executed_at": latest_execution.created_at.isoformat() if latest_execution else None,
            "total_executions": len(team.executions),
            "active_roles": len([r for r in team.roles if r.is_active])
        }
    except Exception as e:
        logger.error(f"Error getting team status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{team_id}/activity")
def get_team_activity(
    team_id: int,
    limit: int = 10,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get recent activity for a team."""
    try:
        # Verify team ownership
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        activities = []
        
        # Team configuration updates (from updated_at)
        if team.updated_at != team.created_at:
            activities.append({
                "type": "team_updated",
                "message": "Team configuration updated",
                "timestamp": team.updated_at.isoformat(),
                "icon": "settings"
            })
        
        # Role modifications
        for role in team.roles:
            if role.updated_at != role.created_at:
                activities.append({
                    "type": "role_modified",
                    "message": f"Role '{role.title}' modified",
                    "timestamp": role.updated_at.isoformat(),
                    "icon": "user-edit"
                })
        
        # Team executions
        if team.executions:
            for execution in sorted(team.executions, key=lambda x: x.created_at, reverse=True)[:limit]:
                status_message = {
                    "SUCCESS": "completed successfully",
                    "FAILED": "failed with errors", 
                    "RUNNING": "is currently running",
                    "PENDING": "is pending execution"
                }.get(execution.status, "updated")
                
                activities.append({
                    "type": "execution",
                    "message": f"Team execution {status_message}",
                    "timestamp": execution.created_at.isoformat(),
                    "icon": "play-circle",
                    "metadata": {
                        "execution_id": execution.id,
                        "status": execution.status,
                        "cost": float(execution.cost) if execution.cost else 0.0
                    }
                })
        
        # Sort by timestamp (most recent first) and limit results
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        # If no activities, add default messages
        if not activities:
            activities = [
                {
                    "type": "team_created",
                    "message": "Team created",
                    "timestamp": team.created_at.isoformat(),
                    "icon": "plus-circle"
                },
                {
                    "type": "info",
                    "message": "Ready for first execution",
                    "timestamp": team.created_at.isoformat(),
                    "icon": "info-circle"
                }
            ]
        
        return {
            "team_id": team_id,
            "activities": activities,
            "total_count": len(activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team activity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{team_id}/roles")
def get_team_roles(
    team_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all roles for a specific team."""
    try:
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        roles_data = []
        for role in team.roles:
            roles_data.append({
                "id": role.id,
                "team_id": role.team_id,
                "title": role.title,
                "description": role.description,
                "expertise": role.expertise.value,
                "llm_model": role.llm_model,
                "llm_config": role.llm_config,
                "agent_config": role.agent_config,
                "is_active": role.is_active,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat()
            })
        
        return {
            "team_id": team_id,
            "roles": roles_data,
            "total_roles": len(roles_data),
            "active_roles": len([r for r in roles_data if r["is_active"]])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{team_id}/roles")
def add_team_role(
    team_id: int,
    role_data: RoleCreate,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Add a new role to a team."""
    try:
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Create new role
        new_role = Role(
            team_id=team_id,
            title=role_data.title,
            description=role_data.description,
            expertise=role_data.expertise,
            llm_model=role_data.llm_model,
            llm_config=role_data.llm_config,
            agent_config=role_data.agent_config,
            is_active=True
        )
        
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        
        return {
            "id": new_role.id,
            "team_id": new_role.team_id,
            "title": new_role.title,
            "description": new_role.description,
            "expertise": new_role.expertise.value,
            "llm_model": new_role.llm_model,
            "llm_config": new_role.llm_config,
            "agent_config": new_role.agent_config,
            "is_active": new_role.is_active,
            "created_at": new_role.created_at.isoformat(),
            "updated_at": new_role.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding team role: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{team_id}/roles/{role_id}")
def update_team_role(
    team_id: int,
    role_id: int,
    role_data: RoleCreate, # Changed from RoleUpdate to RoleCreate to match add_team_role
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a specific role in a team."""
    try:
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Find the role
        role = db.query(Role).filter(
            Role.id == role_id,
            Role.team_id == team_id
        ).first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Update role fields
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        
        role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(role)
        
        return {
            "id": role.id,
            "team_id": role.team_id,
            "title": role.title,
            "description": role.description,
            "expertise": role.expertise.value,
            "llm_model": role.llm_model,
            "llm_config": role.llm_config,
            "agent_config": role.agent_config,
            "is_active": role.is_active,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team role: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{team_id}/roles/{role_id}")
def delete_team_role(
    team_id: int,
    role_id: int,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
):
    """Delete a specific role from a team."""
    try:
        team = TeamService.get_team_by_id(db, team_id, current_user)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Find the role
        role = db.query(Role).filter(
            Role.id == role_id,
            Role.team_id == team_id
        ).first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if team would have any roles left
        remaining_roles = db.query(Role).filter(
            Role.team_id == team_id,
            Role.id != role_id,
            Role.is_active == True
        ).count()
        
        if remaining_roles == 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the last active role from a team"
            )
        
        db.delete(role)
        db.commit()
        
        return {"message": "Role deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team role: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models/available")
def get_available_models() -> Dict[str, Any]:
    """Get available LLM models with metadata."""
    models = {
        "openai": {
            "gpt-4": {
                "name": "GPT-4",
                "description": "Most capable GPT model, best for complex reasoning",
                "cost_per_1k_tokens": 0.03,
                "max_tokens": 8192,
                "capabilities": ["reasoning", "coding", "analysis", "creative"],
                "provider": "openai"
            },
            "gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "description": "Faster and more efficient GPT-4 variant",
                "cost_per_1k_tokens": 0.01,
                "max_tokens": 128000,
                "capabilities": ["reasoning", "coding", "analysis", "creative"],
                "provider": "openai"
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "description": "Fast and cost-effective for most tasks",
                "cost_per_1k_tokens": 0.002,
                "max_tokens": 4096,
                "capabilities": ["coding", "analysis", "creative"],
                "provider": "openai"
            }
        },
        "anthropic": {
            "claude-3-opus": {
                "name": "Claude 3 Opus",
                "description": "Most capable Claude model for complex tasks",
                "cost_per_1k_tokens": 0.015,
                "max_tokens": 200000,
                "capabilities": ["reasoning", "coding", "analysis", "creative"],
                "provider": "anthropic"
            },
            "claude-3-sonnet": {
                "name": "Claude 3 Sonnet",
                "description": "Balanced performance and cost",
                "cost_per_1k_tokens": 0.003,
                "max_tokens": 200000,
                "capabilities": ["reasoning", "coding", "analysis", "creative"],
                "provider": "anthropic"
            },
            "claude-3-haiku": {
                "name": "Claude 3 Haiku",
                "description": "Fastest and most cost-effective Claude",
                "cost_per_1k_tokens": 0.00025,
                "max_tokens": 200000,
                "capabilities": ["coding", "analysis", "creative"],
                "provider": "anthropic"
            }
        },
        "ollama": {
            "deepseek-coder:6.7b": {
                "name": "DeepSeek Coder 6.7B",
                "description": "Specialized coding model, runs locally",
                "cost_per_1k_tokens": 0.0,  # Free when running locally
                "max_tokens": 4096,
                "capabilities": ["coding", "analysis"],
                "provider": "ollama",
                "local": True
            },
            "deepseek-coder:33b": {
                "name": "DeepSeek Coder 33B",
                "description": "Larger coding model with better reasoning",
                "cost_per_1k_tokens": 0.0,
                "max_tokens": 4096,
                "capabilities": ["coding", "analysis", "reasoning"],
                "provider": "ollama",
                "local": True
            },
            "llama2:7b": {
                "name": "Llama 2 7B",
                "description": "General purpose model, good balance",
                "cost_per_1k_tokens": 0.0,
                "max_tokens": 4096,
                "capabilities": ["coding", "analysis", "creative"],
                "provider": "ollama",
                "local": True
            },
            "mistral:7b": {
                "name": "Mistral 7B",
                "description": "Fast and efficient general model",
                "cost_per_1k_tokens": 0.0,
                "max_tokens": 8192,
                "capabilities": ["coding", "analysis", "creative"],
                "provider": "ollama",
                "local": True
            }
        }
    }
    
    return {
        "models": models,
        "providers": {
            "openai": "Cloud-based, paid per token",
            "anthropic": "Cloud-based, paid per token", 
            "ollama": "Local deployment, free to run"
        }
    }


@router.get("/templates/available")
def get_team_templates() -> Dict[str, Any]:
    """Get available team templates for quick setup."""
    templates = {
        "startup_mvp": {
            "name": "Startup MVP Team",
            "description": "Perfect for building a minimum viable product",
            "budget_range": {"min": 50, "max": 200},
            "roles": [
                {
                    "title": "Product Manager",
                    "description": "Defines product vision and requirements",
                    "expertise": "senior",
                    "llm_model": "gpt-4",
                    "agent_config": {
                        "backstory": "You are an experienced product manager who excels at defining clear product requirements and user stories.",
                        "goal": "Create detailed product specifications and user stories"
                    }
                },
                {
                    "title": "Full Stack Developer",
                    "description": "Builds the complete application",
                    "expertise": "senior",
                    "llm_model": "deepseek-coder:6.7b",
                    "agent_config": {
                        "backstory": "You are a skilled full-stack developer who can build complete applications from frontend to backend.",
                        "goal": "Implement the complete application based on requirements"
                    }
                },
                {
                    "title": "UI/UX Designer",
                    "description": "Creates user interface and experience",
                    "expertise": "intermediate",
                    "llm_model": "gpt-3.5-turbo",
                    "agent_config": {
                        "backstory": "You are a creative UI/UX designer who focuses on user-centered design principles.",
                        "goal": "Design intuitive and beautiful user interfaces"
                    }
                }
            ]
        },
        "data_science": {
            "name": "Data Science Team",
            "description": "For data analysis and machine learning projects",
            "budget_range": {"min": 100, "max": 500},
            "roles": [
                {
                    "title": "Data Scientist",
                    "description": "Analyzes data and builds ML models",
                    "expertise": "expert",
                    "llm_model": "gpt-4",
                    "agent_config": {
                        "backstory": "You are a senior data scientist with expertise in statistical analysis and machine learning.",
                        "goal": "Analyze data and build predictive models"
                    }
                },
                {
                    "title": "Data Engineer",
                    "description": "Builds data pipelines and infrastructure",
                    "expertise": "senior",
                    "llm_model": "deepseek-coder:6.7b",
                    "agent_config": {
                        "backstory": "You are a data engineer who specializes in building scalable data pipelines and ETL processes.",
                        "goal": "Design and implement data infrastructure"
                    }
                },
                {
                    "title": "Business Analyst",
                    "description": "Translates business needs into data requirements",
                    "expertise": "intermediate",
                    "llm_model": "claude-3-sonnet",
                    "agent_config": {
                        "backstory": "You are a business analyst who bridges the gap between business needs and technical solutions.",
                        "goal": "Define business requirements and success metrics"
                    }
                }
            ]
        },
        "content_creation": {
            "name": "Content Creation Team",
            "description": "For marketing and content development",
            "budget_range": {"min": 30, "max": 150},
            "roles": [
                {
                    "title": "Content Strategist",
                    "description": "Plans content strategy and messaging",
                    "expertise": "senior",
                    "llm_model": "gpt-4",
                    "agent_config": {
                        "backstory": "You are a content strategist who develops compelling content plans and messaging strategies.",
                        "goal": "Create content strategies and editorial calendars"
                    }
                },
                {
                    "title": "Copywriter",
                    "description": "Writes compelling copy and content",
                    "expertise": "intermediate",
                    "llm_model": "claude-3-sonnet",
                    "agent_config": {
                        "backstory": "You are a skilled copywriter who creates engaging and persuasive content.",
                        "goal": "Write compelling copy for various channels"
                    }
                },
                {
                    "title": "Social Media Manager",
                    "description": "Manages social media presence and engagement",
                    "expertise": "intermediate",
                    "llm_model": "gpt-3.5-turbo",
                    "agent_config": {
                        "backstory": "You are a social media manager who creates engaging content and manages community engagement.",
                        "goal": "Create social media content and engagement strategies"
                    }
                }
            ]
        },
        "custom": {
            "name": "Custom Team",
            "description": "Build your own team from scratch",
            "budget_range": {"min": 20, "max": 1000},
            "roles": []
        }
    }
    
    return {
        "templates": templates,
        "categories": {
            "startup_mvp": "Product Development",
            "data_science": "Data & Analytics", 
            "content_creation": "Marketing & Content",
            "custom": "Custom"
        }
    } 