from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import structlog

from ..models.space import TeamSpace
from ..models.team import Team
from ..models.role import Role
from ..models.execution import TeamExecution
from ..schemas.space import SpaceCreate, SpaceUpdate, SpaceBillingResponse, SpaceActivityResponse

logger = structlog.get_logger()

class SpaceService:
    """Service for managing team spaces"""
    
    @staticmethod
    def create_space_for_team(team_id: int, space_data: SpaceCreate, db: Session) -> TeamSpace:
        """Create a new space for an existing team"""
        try:
            space = TeamSpace(
                id=f"space_{uuid.uuid4()}",
                team_id=team_id,
                name=space_data.name,
                description=space_data.description,
                settings=space_data.settings.dict() if space_data.settings else {},
                storage_config=space_data.storage_config or {}
            )
            
            db.add(space)
            db.flush()  # Get the space ID
            
            # Update team with space_id
            team = db.query(Team).filter(Team.id == team_id).first()
            if team:
                team.space_id = space.id
                
                # Update existing roles with space_id
                roles = db.query(Role).filter(Role.team_id == team_id).all()
                for role in roles:
                    role.space_id = space.id
                
                # Update existing executions with space_id
                executions = db.query(TeamExecution).filter(TeamExecution.team_id == team_id).all()
                for execution in executions:
                    execution.space_id = space.id
            
            db.commit()
            logger.info(f"Space created successfully: {space.name} for team {team_id}")
            return space
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create space for team {team_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_space_by_id(space_id: str, db: Session) -> Optional[TeamSpace]:
        """Get space by ID"""
        return db.query(TeamSpace).filter(TeamSpace.id == space_id).first()
    
    @staticmethod
    def get_space_by_team_id(team_id: int, db: Session) -> Optional[TeamSpace]:
        """Get space by team ID"""
        return db.query(TeamSpace).filter(TeamSpace.team_id == team_id).first()
    
    @staticmethod
    def get_user_spaces(user_id: str, db: Session, skip: int = 0, limit: int = 100) -> List[TeamSpace]:
        """Get all spaces accessible to a user"""
        return db.query(TeamSpace).join(Team).filter(
            Team.auth_owner_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_space(space_id: str, space_data: SpaceUpdate, db: Session) -> Optional[TeamSpace]:
        """Update space configuration"""
        try:
            space = db.query(TeamSpace).filter(TeamSpace.id == space_id).first()
            if not space:
                return None
            
            update_data = space_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "settings" and value:
                    # Merge settings instead of replacing
                    current_settings = space.settings or {}
                    current_settings.update(value)
                    setattr(space, field, current_settings)
                else:
                    setattr(space, field, value)
            
            space.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Space updated successfully: {space_id}")
            return space
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update space {space_id}: {str(e)}")
            raise
    
    @staticmethod
    def configure_storage(space_id: str, storage_config: Dict[str, Any], db: Session) -> Optional[TeamSpace]:
        """Configure external storage for a space"""
        try:
            space = db.query(TeamSpace).filter(TeamSpace.id == space_id).first()
            if not space:
                return None
            
            space.storage_config = storage_config
            space.updated_at = datetime.utcnow()
            
            # Update settings to reflect storage type
            if storage_config.get("type") != "local":
                space.settings["storage"]["type"] = storage_config["type"]
                space.settings["storage"]["external_providers"] = [storage_config["type"]]
            
            db.commit()
            logger.info(f"Storage configured for space {space_id}: {storage_config.get('type')}")
            return space
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to configure storage for space {space_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_space_billing(space_id: str, db: Session) -> Optional[SpaceBillingResponse]:
        """Get billing information for a space"""
        try:
            space = db.query(TeamSpace).filter(TeamSpace.id == space_id).first()
            if not space:
                return None
            
            # Calculate current month spend from executions
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            executions = db.query(TeamExecution).filter(
                and_(
                    TeamExecution.space_id == space_id,
                    TeamExecution.created_at >= start_of_month
                )
            ).all()
            
            current_spend = sum(execution.cost or 0 for execution in executions)
            monthly_budget = space.settings.get("quotas", {}).get("monthly_budget", 500.0)
            usage_percentage = (current_spend / monthly_budget * 100) if monthly_budget > 0 else 0
            
            # Calculate costs by agent
            agent_costs = {}
            for execution in executions:
                for task_execution in execution.task_executions:
                    role_name = task_execution.role.title if task_execution.role else "Unknown"
                    agent_costs[role_name] = agent_costs.get(role_name, 0) + (task_execution.cost or 0)
            
            return SpaceBillingResponse(
                space_id=space_id,
                current_month_spend=current_spend,
                monthly_budget=monthly_budget,
                usage_percentage=usage_percentage,
                agent_costs=agent_costs,
                storage_costs=0.0,  # TODO: Implement storage cost calculation
                execution_costs=current_spend,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to get billing for space {space_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_space_activity(space_id: str, db: Session, limit: int = 50) -> Optional[SpaceActivityResponse]:
        """Get recent activity for a space"""
        try:
            # Get recent executions
            executions = db.query(TeamExecution).filter(
                TeamExecution.space_id == space_id
            ).order_by(desc(TeamExecution.created_at)).limit(limit).all()
            
            activities = []
            for execution in executions:
                activities.append({
                    "type": "execution",
                    "id": execution.id,
                    "status": execution.status.value,
                    "created_at": execution.created_at,
                    "completed_at": execution.completed_at,
                    "cost": execution.cost,
                    "team_name": execution.team.name if execution.team else "Unknown"
                })
            
            # Get recent role changes
            recent_roles = db.query(Role).filter(
                and_(
                    Role.space_id == space_id,
                    Role.updated_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).order_by(desc(Role.updated_at)).limit(10).all()
            
            for role in recent_roles:
                activities.append({
                    "type": "role_update",
                    "id": role.id,
                    "title": role.title,
                    "updated_at": role.updated_at,
                    "is_active": role.is_active
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x.get("created_at") or x.get("updated_at"), reverse=True)
            
            return SpaceActivityResponse(
                space_id=space_id,
                activities=activities[:limit],
                total_activities=len(activities),
                last_activity=activities[0].get("created_at") or activities[0].get("updated_at") if activities else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get activity for space {space_id}: {str(e)}")
            return None
    
    @staticmethod
    def delete_space(space_id: str, db: Session) -> bool:
        """Delete a space (cascade deletes team and all related data)"""
        try:
            space = db.query(TeamSpace).filter(TeamSpace.id == space_id).first()
            if not space:
                return False
            
            # Delete the space (cascade will handle team, roles, executions)
            db.delete(space)
            db.commit()
            
            logger.info(f"Space deleted successfully: {space_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete space {space_id}: {str(e)}")
            raise 