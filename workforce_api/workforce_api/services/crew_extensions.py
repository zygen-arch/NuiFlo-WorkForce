"""CrewAI extensions with database integration and execution tracking."""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from crewai import Agent, Task, Crew, Process
from sqlalchemy.orm import Session

from ..models import Role, TeamExecution, TaskExecution, TeamStatus
from ..core.database import SessionLocal, get_db
import structlog

logger = structlog.get_logger()


class NuiFloAgent(Agent):
    """
    Enhanced Agent that extends CrewAI's Agent with database tracking.
    
    This agent tracks execution metrics and integrates with the database
    for cost monitoring and audit trails.
    """
    
    def __init__(
        self,
        role_model: Role,
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize NuiFloAgent from database Role model.
        
        Args:
            role_model: Database Role containing agent configuration
            team_execution_id: ID of current team execution for tracking
            **kwargs: Additional CrewAI Agent parameters
        """
        # Extract role details
        role = role_model.title
        goal = f"Expert {role_model.expertise.value} level {role_model.title}"
        backstory = (
            f"You are a {role_model.expertise.value} level {role_model.title} "
            f"with extensive experience in your field. {role_model.description or ''}"
        )
        
        # Configure LLM
        llm_config = role_model.llm_config or {}
        llm = role_model.llm_model
        
        # Merge agent configuration
        agent_config = role_model.agent_config or {}
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
            **{**agent_config, **kwargs}
        )
        
        # Store NuiFlo-specific data
        self.role_model = role_model
        self.team_execution_id = team_execution_id
        self.execution_metrics = {
            "tokens_used": 0,
            "cost": Decimal("0.00"),
            "start_time": None,
            "end_time": None,
        }
    
    def track_execution_start(self):
        """Start tracking execution metrics."""
        self.execution_metrics["start_time"] = datetime.utcnow()
        logger.info("Agent execution started", 
                   agent_role=self.role_model.title,
                   team_execution_id=self.team_execution_id)
    
    def track_execution_end(self, tokens_used: int = 0, cost: Decimal = Decimal("0.00")):
        """End tracking and update metrics."""
        self.execution_metrics["end_time"] = datetime.utcnow()
        self.execution_metrics["tokens_used"] += tokens_used
        self.execution_metrics["cost"] += cost
        
        duration = None
        if self.execution_metrics["start_time"]:
            duration = (self.execution_metrics["end_time"] - self.execution_metrics["start_time"]).total_seconds()
        
        logger.info("Agent execution completed",
                   agent_role=self.role_model.title,
                   tokens_used=tokens_used,
                   cost=float(cost),
                   duration_seconds=duration)


class NuiFloTask(Task):
    """
    Enhanced Task that extends CrewAI's Task with database tracking.
    
    This task tracks execution details and stores results in the database.
    """
    
    def __init__(
        self,
        description: str,
        expected_output: str,
        agent: NuiFloAgent,
        task_name: str,
        task_description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize NuiFloTask with tracking capabilities.
        
        Args:
            description: Task description for execution
            expected_output: Expected output format
            agent: NuiFloAgent to execute this task
            task_name: Name for database tracking
            task_description: Optional detailed description
            **kwargs: Additional CrewAI Task parameters
        """
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            **kwargs
        )
        
        self.task_name = task_name
        self.task_description = task_description
        self.nuiflo_agent = agent
        self.execution_id: Optional[int] = None
    
    def save_to_database(
        self,
        session: Session,
        team_execution_id: int,
        status: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        tokens_used: int = 0,
        cost: Decimal = Decimal("0.00"),
        duration_seconds: Optional[float] = None
    ):
        """Save task execution to database."""
        task_execution = TaskExecution(
            team_execution_id=team_execution_id,
            role_id=self.nuiflo_agent.role_model.id,
            task_name=self.task_name,
            task_description=self.task_description,
            status=status,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message,
            tokens_used=tokens_used,
            cost=cost,
            duration_seconds=duration_seconds,
            started_at=self.nuiflo_agent.execution_metrics.get("start_time"),
            completed_at=self.nuiflo_agent.execution_metrics.get("end_time")
        )
        
        session.add(task_execution)
        session.flush()
        self.execution_id = task_execution.id
        
        logger.info("Task execution saved to database",
                   task_id=task_execution.id,
                   task_name=self.task_name,
                   status=status)


class NuiFloCrew(Crew):
    """
    Enhanced Crew that extends CrewAI's Crew with database integration.
    
    This crew manages team execution, tracks costs, and stores results.
    """
    
    def __init__(
        self,
        team_model,  # Team model
        agents: List[NuiFloAgent],
        tasks: List[NuiFloTask],
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize NuiFloCrew with database integration.
        
        Args:
            team_model: Database Team model
            agents: List of NuiFloAgent instances
            tasks: List of NuiFloTask instances
            team_execution_id: Optional team execution ID
            **kwargs: Additional CrewAI Crew parameters
        """
        super().__init__(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,  # Default to sequential
            verbose=True,
            **kwargs
        )
        
        self.team_model = team_model
        self.team_execution_id = team_execution_id
        self.execution_metrics = {
            "total_tokens": 0,
            "total_cost": Decimal("0.00"),
            "start_time": None,
            "end_time": None,
            "task_results": [],
        }
    
    def execute_with_tracking(
        self,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the crew with comprehensive tracking and database storage.
        
        Args:
            inputs: Optional inputs for the crew execution
            
        Returns:
            Dict containing execution results and metrics
        """
        start_time = time.time()
        self.execution_metrics["start_time"] = datetime.utcnow()
        
        # Create database session
        with SessionLocal() as session:
            try:
                # Create team execution record
                team_execution = TeamExecution(
                    team_id=self.team_model.id,
                    status=TeamStatus.RUNNING.value,
                    execution_metadata=inputs or {},
                    started_at=self.execution_metrics["start_time"]
                )
                session.add(team_execution)
                session.flush()
                self.team_execution_id = team_execution.id
                
                logger.info("Team execution started",
                           team_id=self.team_model.id,
                           team_execution_id=team_execution.id)
                
                # Execute the crew using parent class method
                # Note: This is a simplified version - in practice you'd need to
                # integrate more deeply with CrewAI's execution flow
                result = self._execute_crew_with_tracking(session, inputs)
                
                # Calculate total metrics
                end_time = time.time()
                duration = end_time - start_time
                self.execution_metrics["end_time"] = datetime.utcnow()
                self.execution_metrics["duration_seconds"] = duration
                
                # Aggregate metrics from all agents
                total_tokens = 0
                total_cost = Decimal("0.00")
                
                for agent in self.agents:
                    if hasattr(agent, 'execution_metrics'):
                        total_tokens += agent.execution_metrics.get("tokens_used", 0)
                        total_cost += agent.execution_metrics.get("cost", Decimal("0.00"))
                
                self.execution_metrics["total_tokens"] = total_tokens
                self.execution_metrics["total_cost"] = total_cost
                
                # Update team execution record
                team_execution.status = TeamStatus.COMPLETED.value
                team_execution.result = str(result)
                team_execution.completed_at = self.execution_metrics["end_time"]
                team_execution.tokens_used = total_tokens
                team_execution.cost = total_cost
                team_execution.duration_seconds = duration
                
                # Update team's current spend
                self.team_model.current_spend += total_cost
                self.team_model.last_executed_at = self.execution_metrics["end_time"]
                self.team_model.status = TeamStatus.COMPLETED
                
                session.commit()
                
                logger.info("Team execution completed successfully",
                           team_execution_id=team_execution.id,
                           total_tokens=total_tokens,
                           total_cost=float(total_cost),
                           duration=duration)
                
                return {
                    "result": result,
                    "metrics": {
                        "total_tokens": total_tokens,
                        "total_cost": float(total_cost),
                        "duration_seconds": duration,
                        "start_time": self.execution_metrics["start_time"].isoformat(),
                        "end_time": self.execution_metrics["end_time"].isoformat(),
                    },
                    "success": True,
                    "error": None,
                    "team_execution_id": team_execution.id
                }
                
            except Exception as e:
                # Handle execution failure
                end_time = time.time()
                duration = end_time - start_time
                self.execution_metrics["end_time"] = datetime.utcnow()
                
                if hasattr(self, 'team_execution_id') and self.team_execution_id:
                    team_execution.status = TeamStatus.FAILED.value
                    team_execution.error_message = str(e)
                    team_execution.completed_at = self.execution_metrics["end_time"]
                    team_execution.duration_seconds = duration
                    
                    self.team_model.status = TeamStatus.FAILED
                    
                    session.commit()
                
                logger.error("Team execution failed",
                           team_execution_id=getattr(self, 'team_execution_id', None),
                           error=str(e),
                           duration=duration)
                
                return {
                    "result": None,
                    "metrics": {
                        "duration_seconds": duration,
                        "start_time": self.execution_metrics["start_time"].isoformat(),
                        "end_time": self.execution_metrics["end_time"].isoformat(),
                    },
                    "success": False,
                    "error": str(e),
                    "team_execution_id": getattr(self, 'team_execution_id', None)
                }
    
    def _execute_crew_with_tracking(self, session: Session, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Internal method to execute crew with agent and task tracking.
        
        This is a simplified implementation. In a production system,
        you'd want to integrate more deeply with CrewAI's execution engine.
        """
        results = []
        
        for i, (agent, task) in enumerate(zip(self.agents, self.tasks)):
            try:
                # Track agent execution
                agent.track_execution_start()
                
                # Simulate task execution (replace with actual CrewAI integration)
                task_result = f"Task {task.task_name} completed by {agent.role_model.title}"
                
                # Simulate some metrics (replace with actual LLM metrics)
                estimated_tokens = len(task_result) * 2  # Rough estimate
                estimated_cost = Decimal(str(estimated_tokens * 0.0001))  # $0.0001 per token
                
                agent.track_execution_end(
                    tokens_used=estimated_tokens,
                    cost=estimated_cost
                )
                
                # Save task execution to database
                task.save_to_database(
                    session=session,
                    team_execution_id=self.team_execution_id,
                    status=TeamStatus.COMPLETED.value,
                    input_data=inputs,
                    output_data={"result": task_result},
                    tokens_used=estimated_tokens,
                    cost=estimated_cost,
                    duration_seconds=(
                        agent.execution_metrics["end_time"] - 
                        agent.execution_metrics["start_time"]
                    ).total_seconds()
                )
                
                results.append(task_result)
                
            except Exception as e:
                logger.error("Task execution failed",
                           task_name=task.task_name,
                           agent_role=agent.role_model.title,
                           error=str(e))
                
                # Save failed task to database
                task.save_to_database(
                    session=session,
                    team_execution_id=self.team_execution_id,
                    status=TeamStatus.FAILED.value,
                    input_data=inputs,
                    error_message=str(e)
                )
                
                raise e
        
        return "\n".join(results)


def create_crew_from_team(team_model) -> NuiFloCrew:
    """
    Factory function to create a NuiFloCrew from a database Team model.
    
    Args:
        team_model: Database Team model with roles loaded
        
    Returns:
        Configured NuiFloCrew instance
    """
    # Create agents from team roles
    agents = []
    for role in team_model.roles:
        if role.is_active:
            agent = NuiFloAgent(role_model=role)
            agents.append(agent)
    
    if not agents:
        raise ValueError(f"Team {team_model.name} has no active roles")
    
    # Create tasks for each agent
    tasks = []
    for i, agent in enumerate(agents):
        task_description = (
            f"Work as a {agent.role_model.title} to contribute to the team's objectives. "
            f"Apply your {agent.role_model.expertise.value} level expertise to analyze "
            f"and provide insights from your perspective."
        )
        
        task = NuiFloTask(
            description=task_description,
            expected_output="Detailed analysis and recommendations from your expertise area",
            agent=agent,
            task_name=f"Task_{i+1}_{agent.role_model.title.replace(' ', '_')}",
            task_description=task_description
        )
        tasks.append(task)
    
    # Create and return the crew
    crew = NuiFloCrew(
        team_model=team_model,
        agents=agents,
        tasks=tasks
    )
    
    return crew 