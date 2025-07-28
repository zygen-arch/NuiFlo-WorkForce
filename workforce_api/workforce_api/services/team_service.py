"""Team management service with business logic."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Team, Role, TeamStatus, ExpertiseLevel
from ..core.database import SessionLocal
# from .hybrid_crew_extensions import create_hybrid_crew_from_team  # Temporarily disabled
import structlog

logger = structlog.get_logger()


class TeamService:
    """Enhanced team management service with intelligent routing capabilities"""
    
    @staticmethod
    def create_team(
        name: str,
        owner_id: str,  # UUID from Supabase
        monthly_budget: Decimal,
        description: Optional[str] = None,
        roles_data: Optional[List[Dict[str, Any]]] = None,
        session: Optional[Session] = None
    ) -> Team:
        """Create a new team with roles"""
        
        def _create_team_internal(db: Session) -> Team:
            team = Team(
                name=name,
                auth_owner_id=owner_id,  # UUID from Supabase
                description=description,
                monthly_budget=monthly_budget,
                status=TeamStatus.IDLE
            )
            
            db.add(team)
            db.flush()  # Get the team ID
            
            # Add roles if provided
            if roles_data:
                for role_data in roles_data:
                    role = Role(
                        team_id=team.id,
                        title=role_data.get('title', 'Team Member'),
                        description=role_data.get('description', ''),
                        expertise=ExpertiseLevel[role_data.get('expertise', 'INTERMEDIATE').upper()],
                        llm_model=role_data.get('llm_model', 'gpt-3.5-turbo'),
                        system_prompt=role_data.get('system_prompt', ''),
                        is_active=role_data.get('is_active', True)
                    )
                    db.add(role)
            
            db.commit()
            db.refresh(team)
            logger.info(f"Team created successfully: {team.name}", team_id=team.id)
            return team
        
        if session:
            return _create_team_internal(session)
        else:
            with SessionLocal() as db:
                return _create_team_internal(db)
    
    @staticmethod
    def get_team(team_id: int, session: Optional[Session] = None) -> Optional[Team]:
        """Get team by ID"""
        def _get_team_internal(db: Session) -> Optional[Team]:
            return db.query(Team).filter(Team.id == team_id).first()
        
        if session:
            return _get_team_internal(session)
        else:
            with SessionLocal() as db:
                return _get_team_internal(db)
    
    @staticmethod
    def list_user_teams(owner_id: str, session: Optional[Session] = None) -> List[Team]:
        """List all teams for a user"""
        def _list_teams_internal(db: Session) -> List[Team]:
            return db.query(Team).filter(Team.auth_owner_id == owner_id).all()
        
        if session:
            return _list_teams_internal(session)
        else:
            with SessionLocal() as db:
                return _list_teams_internal(db)
    
    @staticmethod
    def update_team(
        team_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        monthly_budget: Optional[Decimal] = None,
        session: Optional[Session] = None
    ) -> Optional[Team]:
        """Update team details"""
        def _update_team_internal(db: Session) -> Optional[Team]:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                return None
            
            if name is not None:
                team.name = name
            if description is not None:
                team.description = description
            if monthly_budget is not None:
                team.monthly_budget = monthly_budget
            
            team.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(team)
            
            logger.info(f"Team updated successfully: {team.name}", team_id=team.id)
            return team
        
        if session:
            return _update_team_internal(session)
        else:
            with SessionLocal() as db:
                return _update_team_internal(db)
    
    @staticmethod
    def delete_team(team_id: int, session: Optional[Session] = None) -> bool:
        """Delete a team and all associated data"""
        def _delete_team_internal(db: Session) -> bool:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                return False
            
            team_name = team.name
            db.delete(team)
            db.commit()
            
            logger.info(f"Team deleted successfully: {team_name}", team_id=team_id)
            return True
        
        if session:
            return _delete_team_internal(session)
        else:
            with SessionLocal() as db:
                return _delete_team_internal(db)
    
    @staticmethod
    def execute_team(
        team_id: int,
        inputs: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Execute team workflow (minimal version without CrewAI for now)
        
        This will be upgraded to use our hybrid LLM system once dependencies are resolved.
        """
        def _execute_team_internal(db: Session) -> Dict[str, Any]:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            # Update team status
            team.status = TeamStatus.RUNNING
            team.last_executed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Executing team workflow: {team.name}", team_id=team_id)
            
            try:
                # Simulate team execution for now
                # TODO: Replace with actual hybrid CrewAI execution
                result = {
                    "result": f"Team '{team.name}' executed successfully with {len(team.roles)} agents.",
                    "success": True,
                    "metrics": {
                        "execution_time_seconds": 2.5,
                        "total_cost": 0.0,  # Free simulation
                        "total_savings": 0.15,  # Simulated savings vs GPT-4
                        "efficiency_score": 100.0,  # 100% free calls
                        "agents_performance": {
                            role.title: {
                                "status": "completed",
                                "cost": 0.0,
                                "savings": 0.05
                            } for role in team.roles if role.is_active
                        }
                    },
                    "team_execution_id": None,
                    "cost_summary": "💰 Spent $0.00, Saved $0.15 (100% FREE simulation!)"
                }
                
                # Update team status
                team.status = TeamStatus.COMPLETED
                db.commit()
                
                logger.info(f"Team execution completed: {team.name}", 
                           team_id=team_id, 
                           result_preview=result["result"][:100])
                
                return result
                
            except Exception as e:
                # Update team status on error
                team.status = TeamStatus.FAILED
                db.commit()
                
                logger.error(f"Team execution failed: {team.name}", 
                           team_id=team_id, 
                           error=str(e))
                
                return {
                    "result": f"Team execution failed: {str(e)}",
                    "success": False,
                    "error": str(e),
                    "metrics": {
                        "execution_time_seconds": 0,
                        "total_cost": 0.0,
                        "total_savings": 0.0,
                        "efficiency_score": 0.0
                    }
                }
        
        if session:
            return _execute_team_internal(session)
        else:
            with SessionLocal() as db:
                return _execute_team_internal(db)
    
    @staticmethod
    def get_team_status(team_id: int, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """Get current team execution status"""
        def _get_status_internal(db: Session) -> Optional[Dict[str, Any]]:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                return None
            
            return {
                "team_id": team.id,
                "name": team.name,
                "status": team.status.value,
                "last_executed_at": team.last_executed_at.isoformat() if team.last_executed_at else None,
                "active_roles": len([r for r in team.roles if r.is_active]),
                "total_roles": len(team.roles),
                "monthly_budget": float(team.monthly_budget),
                "current_spend": float(team.current_spend)
            }
        
        if session:
            return _get_status_internal(session)
        else:
            with SessionLocal() as db:
                return _get_status_internal(db) 