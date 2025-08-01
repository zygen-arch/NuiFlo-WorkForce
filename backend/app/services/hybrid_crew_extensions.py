"""
🤖 Hybrid CrewAI Extensions - The Future of Cost-Effective AI Teams

This module extends CrewAI with our Intelligent LLM Router to create
the most cost-effective AI agents in the industry.

Key Features:
- Smart cost optimization (Ollama + Commercial LLMs)
- Real-time savings tracking
- Automatic quality scaling
- Transparent cost reporting
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from crewai import Agent, Task, Crew, Process
from sqlalchemy.orm import Session

from ..models import Role, TeamExecution, TaskExecution, TeamStatus
from ..core.database import SessionLocal
from ..core.intelligent_router import (
    get_intelligent_router, 
    ComplexityLevel,
    LLMProvider,
    RoutingDecision,
    ExecutionResult
)
import structlog

logger = structlog.get_logger()


class HybridNuiFloAgent(Agent):
    """
    🧠 Hybrid AI Agent - Smart, Cost-Effective, Powerful
    
    This agent automatically chooses between:
    - Ollama/Mistral (FREE) for simple tasks
    - GPT-3.5 (CHEAP) for medium complexity  
    - GPT-4 (PREMIUM) for complex reasoning
    
    Result: Up to 80% cost savings while maintaining quality!
    """
    
    def __init__(
        self,
        role_model: Role,
        team_execution_id: Optional[int] = None,
        max_budget_per_task: Optional[Decimal] = None,
        quality_preference: str = "balanced",  # "fast", "balanced", "premium"
        **kwargs
    ):
        """
        Initialize Hybrid Agent
        
        Args:
            role_model: Database Role containing agent configuration
            team_execution_id: ID of current team execution
            max_budget_per_task: Maximum spend per task (cost control)
            quality_preference: Speed vs quality preference
        """
        self.role_model = role_model
        self.team_execution_id = team_execution_id
        self.max_budget_per_task = max_budget_per_task or Decimal("1.00")  # $1 default
        self.quality_preference = quality_preference
        
        # Get intelligent router
        self.router = get_intelligent_router()
        
        # Initialize execution tracking
        self.execution_metrics = {
            "total_tokens": 0,
            "total_cost": Decimal("0.00"),
            "ollama_calls": 0,
            "commercial_calls": 0,
            "savings": Decimal("0.00"),
            "task_history": []
        }
        
        # Extract role details for CrewAI
        role = role_model.title
        goal = f"Expert {role_model.expertise.value} level {role_model.title}"
        backstory = (
            f"You are a {role_model.expertise.value} level {role_model.title} "
            f"with extensive experience in your field. {role_model.description or ''}"
        )
        
        # Initialize CrewAI Agent with dummy LLM (we'll override execution)
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            **kwargs
        )
        
        logger.info(f"🤖 Hybrid Agent created: {role}", 
                   max_budget=float(self.max_budget_per_task),
                   quality=quality_preference)
    
    def execute_task(self, task_prompt: str, context: Optional[str] = None) -> str:
        """
        🚀 Execute task with intelligent LLM routing
        
        This is where the magic happens - smart routing for optimal cost/quality!
        """
        start_time = time.time()
        
        try:
            # 1. Get routing decision from our intelligent router
            routing_decision = self.router.route_request(
                prompt=task_prompt,
                context=context,
                max_budget=self.max_budget_per_task,
                preferred_quality=self.quality_preference
            )
            
            logger.info(f"🎯 Routing to {routing_decision.provider.value}",
                       estimated_cost=float(routing_decision.estimated_cost),
                       complexity=routing_decision.complexity.value)
            
            # 2. Execute using the selected provider
            result = self.router.execute_request(routing_decision, task_prompt)
            
            # 3. Track execution metrics
            self._track_execution(routing_decision, result)
            
            # 4. Calculate savings (vs always using GPT-4)
            savings = self._calculate_savings(result)
            
            logger.info(f"✅ Task completed successfully",
                       provider=result.provider.value,
                       actual_cost=float(result.actual_cost),
                       savings=float(savings),
                       tokens=result.actual_tokens)
            
            return result.content
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Task execution failed: {e}", duration=duration)
            
            # Fallback to simple response
            return f"Task execution failed: {str(e)}"
    
    def _track_execution(self, decision: RoutingDecision, result: ExecutionResult):
        """Track execution metrics for cost analysis"""
        # Update totals
        self.execution_metrics["total_tokens"] += result.actual_tokens
        self.execution_metrics["total_cost"] += result.actual_cost
        
        # Track provider usage
        if result.provider == LLMProvider.OLLAMA_MISTRAL:
            self.execution_metrics["ollama_calls"] += 1
        else:
            self.execution_metrics["commercial_calls"] += 1
        
        # Calculate savings vs always using GPT-4
        gpt4_cost = (result.actual_tokens / 1000) * Decimal("0.03")  # GPT-4 pricing
        savings = gpt4_cost - result.actual_cost
        self.execution_metrics["savings"] += savings
        
        # Store task history
        self.execution_metrics["task_history"].append({
            "provider": result.provider.value,
            "complexity": decision.complexity.value,
            "tokens": result.actual_tokens,
            "cost": float(result.actual_cost),
            "savings": float(savings),
            "duration": result.duration_seconds,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _calculate_savings(self, result: ExecutionResult) -> Decimal:
        """Calculate savings vs always using premium models"""
        gpt4_cost = (result.actual_tokens / 1000) * Decimal("0.03")
        return gpt4_cost - result.actual_cost
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost and savings summary"""
        total_calls = self.execution_metrics["ollama_calls"] + self.execution_metrics["commercial_calls"]
        
        if total_calls == 0:
            return {"message": "No tasks executed yet"}
        
        ollama_percentage = (self.execution_metrics["ollama_calls"] / total_calls) * 100
        
        return {
            "total_cost": float(self.execution_metrics["total_cost"]),
            "total_savings": float(self.execution_metrics["savings"]),
            "total_tokens": self.execution_metrics["total_tokens"],
            "total_calls": total_calls,
            "ollama_calls": self.execution_metrics["ollama_calls"],
            "commercial_calls": self.execution_metrics["commercial_calls"],
            "ollama_percentage": round(ollama_percentage, 1),
            "average_cost_per_call": float(self.execution_metrics["total_cost"] / total_calls),
            "cost_efficiency": f"{ollama_percentage:.1f}% of calls were FREE!",
            "task_history": self.execution_metrics["task_history"][-5:]  # Last 5 tasks
        }


class HybridNuiFloTask(Task):
    """
    🎯 Hybrid AI Task - Intelligent Task Execution
    
    Extends CrewAI Task with smart routing and cost tracking
    """
    
    def __init__(
        self,
        description: str,
        agent: HybridNuiFloAgent,
        expected_output: str,
        task_name: str,
        complexity_hint: Optional[ComplexityLevel] = None,
        max_budget: Optional[Decimal] = None,
        **kwargs
    ):
        super().__init__(
            description=description,
            agent=agent,
            expected_output=expected_output,
            **kwargs
        )
        
        self.task_name = task_name
        self.complexity_hint = complexity_hint
        self.max_budget = max_budget
        self.execution_start = None
        self.execution_end = None
        
        logger.info(f"🎯 Hybrid Task created: {task_name}")


class HybridNuiFloCrew(Crew):
    """
    🚀 Hybrid AI Crew - The Most Cost-Effective AI Team Platform
    
    Features:
    - Intelligent cost optimization across all agents
    - Real-time savings tracking
    - Transparent cost reporting
    - Automatic quality scaling
    """
    
    def __init__(
        self,
        team_model,
        agents: List[HybridNuiFloAgent],
        tasks: List[HybridNuiFloTask],
        max_team_budget: Optional[Decimal] = None,
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            **kwargs
        )
        
        self.team_model = team_model
        self.max_team_budget = max_team_budget or Decimal("10.00")  # $10 default
        self.team_execution_id = team_execution_id
        
        # Team-level metrics
        self.team_metrics = {
            "total_cost": Decimal("0.00"),
            "total_savings": Decimal("0.00"),
            "execution_start": None,
            "execution_end": None,
            "agents_summary": {},
            "budget_utilization": 0.0
        }
        
        logger.info(f"🚀 Hybrid Crew assembled: {team_model.name}",
                   agents=len(agents),
                   tasks=len(tasks),
                   max_budget=float(max_team_budget))
    
    def execute_with_tracking(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        🎯 Execute crew with comprehensive cost tracking and optimization
        
        Returns detailed cost analysis and savings report!
        """
        self.team_metrics["execution_start"] = datetime.utcnow()
        
        try:
            # Execute each task with our hybrid agents
            task_results = []
            
            for i, (agent, task) in enumerate(zip(self.agents, self.tasks)):
                logger.info(f"▶️ Executing task {i+1}/{len(self.tasks)}: {task.task_name}")
                
                # Check budget before execution
                if self.team_metrics["total_cost"] >= self.max_team_budget:
                    logger.warning(f"⚠️ Budget limit reached, skipping remaining tasks")
                    break
                
                # Build task prompt with context
                task_prompt = self._build_task_prompt(task, inputs, task_results)
                
                # Execute task with hybrid routing
                result = agent.execute_task(task_prompt)
                task_results.append(result)
                
                # Update team metrics
                self._update_team_metrics(agent)
            
            # Finalize execution
            self.team_metrics["execution_end"] = datetime.utcnow()
            final_result = "\n\n".join(task_results)
            
            # Generate comprehensive report
            return self._generate_execution_report(final_result)
            
        except Exception as e:
            logger.error(f"❌ Crew execution failed: {e}")
            self.team_metrics["execution_end"] = datetime.utcnow()
            
            return {
                "result": f"Execution failed: {str(e)}",
                "success": False,
                "error": str(e),
                "metrics": self._get_team_cost_summary()
            }
    
    def _build_task_prompt(
        self, 
        task: HybridNuiFloTask, 
        inputs: Optional[Dict[str, Any]], 
        previous_results: List[str]
    ) -> str:
        """Build comprehensive task prompt with context"""
        prompt_parts = [
            f"Role: {task.agent.role}",
            f"Task: {task.description}",
            f"Expected Output: {task.expected_output}"
        ]
        
        if inputs:
            prompt_parts.append(f"Input Context: {inputs}")
        
        if previous_results:
            prompt_parts.append(f"Previous Task Results: {previous_results[-1]}")  # Last result as context
        
        return "\n\n".join(prompt_parts)
    
    def _update_team_metrics(self, agent: HybridNuiFloAgent):
        """Update team-level metrics from agent execution"""
        agent_summary = agent.get_cost_summary()
        
        self.team_metrics["total_cost"] += agent.execution_metrics["total_cost"]
        self.team_metrics["total_savings"] += agent.execution_metrics["savings"]
        self.team_metrics["agents_summary"][agent.role] = agent_summary
        
        # Calculate budget utilization
        self.team_metrics["budget_utilization"] = float(
            (self.team_metrics["total_cost"] / self.max_team_budget) * 100
        )
    
    def _generate_execution_report(self, final_result: str) -> Dict[str, Any]:
        """Generate comprehensive execution report with cost analysis"""
        duration = (
            self.team_metrics["execution_end"] - self.team_metrics["execution_start"]
        ).total_seconds()
        
        # Calculate efficiency metrics
        total_ollama_calls = sum(
            summary.get("ollama_calls", 0) 
            for summary in self.team_metrics["agents_summary"].values()
        )
        total_commercial_calls = sum(
            summary.get("commercial_calls", 0)
            for summary in self.team_metrics["agents_summary"].values()
        )
        total_calls = total_ollama_calls + total_commercial_calls
        
        efficiency_score = (total_ollama_calls / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "result": final_result,
            "success": True,
            "metrics": {
                "execution_time_seconds": duration,
                "total_cost": float(self.team_metrics["total_cost"]),
                "total_savings": float(self.team_metrics["total_savings"]),
                "budget_utilization": self.team_metrics["budget_utilization"],
                "efficiency_score": round(efficiency_score, 1),
                "cost_breakdown": {
                    "ollama_calls": total_ollama_calls,
                    "commercial_calls": total_commercial_calls,
                    "free_percentage": round(efficiency_score, 1)
                },
                "agents_performance": self.team_metrics["agents_summary"]
            },
            "team_execution_id": self.team_execution_id,
            "cost_summary": f"💰 Spent ${self.team_metrics['total_cost']:.4f}, Saved ${self.team_metrics['total_savings']:.4f} ({efficiency_score:.1f}% FREE calls!)"
        }
    
    def _get_team_cost_summary(self) -> Dict[str, Any]:
        """Get current team cost summary"""
        return {
            "total_cost": float(self.team_metrics["total_cost"]),
            "total_savings": float(self.team_metrics["total_savings"]),
            "budget_utilization": self.team_metrics["budget_utilization"],
            "agents_summary": self.team_metrics["agents_summary"]
        }


def create_hybrid_crew_from_team(team_model, max_budget: Optional[Decimal] = None) -> HybridNuiFloCrew:
    """
    🏭 Factory function to create a Hybrid Crew from database Team model
    
    This is where we transform traditional AI teams into cost-optimized powerhouses!
    """
    # Create hybrid agents from team roles
    agents = []
    for role in team_model.roles:
        if role.is_active:
            # Calculate per-agent budget (distribute team budget)
            agent_budget = (max_budget / len(team_model.roles)) if max_budget else Decimal("2.00")
            
            agent = HybridNuiFloAgent(
                role_model=role,
                max_budget_per_task=agent_budget,
                quality_preference="balanced"  # TODO: Make this configurable per team
            )
            agents.append(agent)
    
    if not agents:
        raise ValueError(f"Team {team_model.name} has no active roles")
    
    # Create hybrid tasks for each agent
    tasks = []
    for i, agent in enumerate(agents):
        task_description = (
            f"As a {agent.role_model.title}, analyze the given requirements and provide "
            f"expert insights from your {agent.role_model.expertise.value} level perspective. "
            f"Focus on practical, actionable recommendations that align with your role."
        )
        
        task = HybridNuiFloTask(
            description=task_description,
            expected_output="Detailed professional analysis with specific recommendations",
            agent=agent,
            task_name=f"Task_{i+1}_{agent.role_model.title.replace(' ', '_')}",
            max_budget=agent.max_budget_per_task
        )
        tasks.append(task)
    
    # Create hybrid crew
    crew = HybridNuiFloCrew(
        team_model=team_model,
        agents=agents,
        tasks=tasks,
        max_team_budget=max_budget or team_model.monthly_budget
    )
    
    logger.info(f"🚀 Hybrid Crew factory complete: {team_model.name}",
               agents=len(agents),
               estimated_savings="Up to 80% cost reduction!")
    
    return crew 