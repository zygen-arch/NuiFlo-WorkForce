"""Team management service with business logic."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import Team, Role, TeamStatus, ExpertiseLevel
from ..core.database import SessionLocal
from .hybrid_crew_extensions import create_hybrid_crew_from_team
import structlog

logger = structlog.get_logger()


class TeamService:
    """Service for team management operations."""
    
    @staticmethod
    def create_team(
        name: str,
        owner_id: str,  # Changed to str for UUID
        monthly_budget: Decimal,
        description: Optional[str] = None,
        roles_data: Optional[List[Dict[str, Any]]] = None,
        session: Optional[Session] = None
    ) -> Team:
        """
        Create a new team with roles.
        
        Args:
            name: Team name
            owner_id: UUID of team owner (from Supabase auth)
            monthly_budget: Monthly budget in USD
            description: Optional team description
            roles_data: List of role configurations
            session: Optional database session
            
        Returns:
            Created Team instance
        """
        def _create_team_internal(db: Session) -> Team:
            # Create team with auth_owner_id
            team = Team(
                name=name,
                auth_owner_id=owner_id,  # UUID from Supabase
                description=description,
                monthly_budget=monthly_budget,
                status=TeamStatus.IDLE
            )
            db.add(team)
            db.flush()  # Get team ID
            
            # Create roles if provided
            if roles_data:
                for role_data in roles_data:
                    role = Role(
                        team_id=team.id,
                        title=role_data["title"],
                        description=role_data.get("description"),
                        expertise=ExpertiseLevel(role_data["expertise"]),
                        llm_model=role_data.get("llm_model", "gpt-3.5-turbo"),
                        llm_config=role_data.get("llm_config"),
                        agent_config=role_data.get("agent_config"),
                        is_active=role_data.get("is_active", True)
                    )
                    db.add(role)
            
            db.commit()
            db.refresh(team)
            
            logger.info("Team created", team_id=team.id, team_name=name, owner_id=owner_id)
            return team
        
        if session:
            return _create_team_internal(session)
        else:
            with SessionLocal() as db:
                return _create_team_internal(db)
    
    @staticmethod
    def get_team_with_roles(
        team_id: int,
        session: Optional[Session] = None
    ) -> Optional[Team]:
        """
        Get team with roles loaded.
        
        Args:
            team_id: Team ID
            session: Optional database session
            
        Returns:
            Team instance with roles or None
        """
        def _get_team_internal(db: Session) -> Optional[Team]:
            stmt = (
                select(Team)
                .options(selectinload(Team.roles))
                .where(Team.id == team_id)
            )
            result = db.execute(stmt)
            return result.scalar_one_or_none()
        
        if session:
            return _get_team_internal(session)
        else:
            with SessionLocal() as db:
                return _get_team_internal(db)
    
    @staticmethod
    def list_user_teams(owner_id: str, session: Optional[Session] = None) -> List[Team]:  # Changed to str
        """
        Get all teams for a user.
        
        Args:
            owner_id: UUID of team owner (from Supabase auth)
            session: Optional database session
            
        Returns:
            List of Team instances
        """
        def _list_teams_internal(db: Session) -> List[Team]:
            result = db.execute(
                select(Team)
                .where(Team.auth_owner_id == owner_id)  # Use auth_owner_id
                .options(selectinload(Team.roles))
                .order_by(Team.created_at.desc())
            )
            return result.scalars().all()
        
        if session:
            return _list_teams_internal(session)
        else:
            with SessionLocal() as db:
                return _list_teams_internal(db)
    
    @staticmethod
    def execute_team(
        team_id: int,
        inputs: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Execute a team using CrewAI integration.
        
        Args:
            team_id: Team ID to execute
            inputs: Optional execution inputs
            session: Optional database session
            
        Returns:
            Execution results and metrics
        """
        def _execute_team_internal(db: Session) -> Dict[str, Any]:
            # Get team with roles
            team = TeamService.get_team_with_roles(team_id, db)
            if not team:
                raise ValueError(f"Team with ID {team_id} not found")
            
            if not team.roles:
                raise ValueError(f"Team {team.name} has no roles configured")
            
            active_roles = [role for role in team.roles if role.is_active]
            if not active_roles:
                raise ValueError(f"Team {team.name} has no active roles")
            
            # Check if team is already running
            if team.status == TeamStatus.RUNNING:
                raise ValueError(f"Team {team.name} is already running")
            
            # Check budget
            if team.current_spend >= team.monthly_budget:
                raise ValueError(f"Team {team.name} has exceeded monthly budget")
            
            # Create and execute crew
            crew = create_hybrid_crew_from_team(team)
            result = crew.execute_with_tracking(inputs)
            
            return result
        
        if session:
            return _execute_team_internal(session)
        else:
            with SessionLocal() as db:
                return _execute_team_internal(db)
    
    @staticmethod
    def update_team(
        team_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        monthly_budget: Optional[Decimal] = None,
        session: Optional[Session] = None
    ) -> Optional[Team]:
        """
        Update team information.
        
        Args:
            team_id: Team ID
            name: Optional new name
            description: Optional new description
            monthly_budget: Optional new budget
            session: Optional database session
            
        Returns:
            Updated Team instance or None
        """
        def _update_team_internal(db: Session) -> Optional[Team]:
            team = TeamService.get_team_with_roles(team_id, db)
            if not team:
                return None
            
            if name is not None:
                team.name = name
            if description is not None:
                team.description = description
            if monthly_budget is not None:
                team.monthly_budget = monthly_budget
            
            db.commit()
            db.refresh(team)
            
            logger.info("Team updated", team_id=team_id)
            return team
        
        if session:
            return _update_team_internal(session)
        else:
            with SessionLocal() as db:
                return _update_team_internal(db)
    
    @staticmethod
    def delete_team(
        team_id: int,
        session: Optional[Session] = None
    ) -> bool:
        """
        Delete a team (if not currently running).
        
        Args:
            team_id: Team ID
            session: Optional database session
            
        Returns:
            True if deleted, False if not found
        """
        def _delete_team_internal(db: Session) -> bool:
            team = TeamService.get_team_with_roles(team_id, db)
            if not team:
                return False
            
            if team.status == TeamStatus.RUNNING:
                raise ValueError(f"Cannot delete team {team.name} while it's running")
            
            db.delete(team)
            db.commit()
            
            logger.info("Team deleted", team_id=team_id, team_name=team.name)
            return True
        
        if session:
            return _delete_team_internal(session)
        else:
            with SessionLocal() as db:
                return _delete_team_internal(db) 