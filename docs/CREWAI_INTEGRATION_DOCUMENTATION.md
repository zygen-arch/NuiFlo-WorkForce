# NuiFlo WorkForce - CrewAI Integration Documentation

## 🤖 Overview

This document provides comprehensive documentation for the CrewAI integration in NuiFlo WorkForce, including custom extensions, workflow execution, and advanced usage patterns.

## 📋 Table of Contents

1. [CrewAI Framework Overview](#-crewai-framework-overview)
2. [NuiFlo Extensions](#-nuiflo-extensions)
3. [Workflow Execution](#-workflow-execution)
4. [Intelligent LLM Integration](#-intelligent-llm-integration)
5. [Advanced Usage Patterns](#-advanced-usage-patterns)
6. [Performance Optimization](#-performance-optimization)

---

## 🏗️ CrewAI Framework Overview

### What is CrewAI?

CrewAI is a cutting-edge framework for orchestrating role-playing, autonomous AI agents. It enables creating teams of AI agents that can collaborate, delegate tasks, and work together to achieve complex goals.

#### Key Concepts

- **Agent**: An AI entity with a specific role, goal, and backstory
- **Task**: A specific job to be completed by an agent
- **Crew**: A team of agents working together on related tasks
- **Process**: The execution flow (sequential, hierarchical, etc.)

#### Basic CrewAI Structure

```python
from crewai import Agent, Task, Crew, Process

# Define agents
agent = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert data analyst with statistical background",
    llm=llm_model
)

# Define tasks
task = Task(
    description="Analyze sales data for Q4 trends",
    agent=agent,
    expected_output="Comprehensive sales analysis report"
)

# Create crew
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential
)

# Execute
result = crew.kickoff()
```

### NuiFlo's CrewAI Enhancements

NuiFlo extends CrewAI with:

1. **Database Integration**: Persistent storage of teams, roles, and executions
2. **Intelligent LLM Routing**: Automatic model selection based on complexity
3. **Cost Tracking**: Real-time monitoring of token usage and costs
4. **Performance Metrics**: Detailed execution analytics
5. **Error Handling**: Robust error recovery and logging
6. **Budget Management**: Automatic budget enforcement

---

## 🔧 NuiFlo Extensions

### Enhanced Agent Class (`NuiFloAgent`)

#### Overview
Extends CrewAI's Agent with database integration and execution tracking.

```python
from workforce_api.services.crew_extensions import NuiFloAgent
from workforce_api.models import Role

class NuiFloAgent(Agent):
    """Enhanced Agent that extends CrewAI's Agent with database tracking."""
    
    def __init__(
        self,
        role_model: Role,
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
        # Initialize from database Role model
        self.role_model = role_model
        self.team_execution_id = team_execution_id
        
        # Auto-configure from role model
        role = role_model.title
        goal = f"Expert {role_model.expertise.value} level {role_model.title}"
        backstory = self._generate_backstory(role_model)
        llm = role_model.llm_model
        
        # Extract agent config
        agent_config = role_model.agent_config or {}
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
            **{**agent_config, **kwargs}
        )
        
        # Initialize tracking
        self.execution_metrics = {
            "tokens_used": 0,
            "cost": Decimal("0.00"),
            "start_time": None,
            "end_time": None,
        }
```

#### Key Features

##### Automatic Configuration
The agent automatically configures itself from the database Role model:

```python
# Role configuration mapping
role_config = {
    "role": role_model.title,
    "goal": f"Expert {role_model.expertise.value} level {role_model.title}",
    "backstory": role_model.agent_config.get("backstory", default_backstory),
    "llm": role_model.llm_model,
    "tools": role_model.agent_config.get("tools", []),
    "allow_delegation": role_model.agent_config.get("allow_delegation", False),
    "verbose": role_model.agent_config.get("verbose", True)
}
```

##### Execution Tracking
Built-in methods for tracking execution metrics:

```python
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
```

#### Usage Example

```python
from workforce_api.models import Role
from workforce_api.services.crew_extensions import NuiFloAgent

# Get role from database
role = db.query(Role).filter(Role.id == 1).first()

# Create enhanced agent
agent = NuiFloAgent(
    role_model=role,
    team_execution_id=123,
    # Additional CrewAI parameters
    max_iter=5,
    max_execution_time=3600
)

# The agent is automatically configured with:
# - role.title as the agent role
# - Generated goal based on expertise level
# - Backstory from agent_config or auto-generated
# - LLM model from role.llm_model
# - Tools and configuration from agent_config

print(f"Created agent: {agent.role}")
print(f"Goal: {agent.goal}")
print(f"LLM: {agent.llm}")
```

### Enhanced Task Class (`NuiFloTask`)

#### Overview
Extends CrewAI's Task with database tracking and metrics collection.

```python
class NuiFloTask(Task):
    """Enhanced Task that extends CrewAI's Task with database tracking."""
    
    def __init__(
        self,
        task_name: str,
        role_id: int,
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
        self.task_name = task_name
        self.role_id = role_id
        self.team_execution_id = team_execution_id
        
        # Initialize execution tracking
        self.execution_metrics = {
            "tokens_used": 0,
            "cost": Decimal("0.00"),
            "start_time": None,
            "end_time": None,
            "success": False,
            "error": None
        }
        
        super().__init__(**kwargs)
```

#### Task Creation Patterns

##### Dynamic Task Generation
```python
def create_task_from_role(role: Role, inputs: Dict[str, Any]) -> NuiFloTask:
    """Create a task dynamically based on role and inputs."""
    
    # Generate task description based on role and inputs
    if role.title.lower() == "content strategist":
        description = f"Develop a comprehensive content strategy for {inputs.get('project_name', 'the project')}"
        expected_output = "A detailed content strategy document with recommendations"
    elif role.title.lower() == "developer":
        description = f"Design and plan the technical architecture for {inputs.get('project_name', 'the project')}"
        expected_output = "Technical architecture document with implementation plan"
    else:
        # Generic task based on role
        description = f"Perform {role.title.lower()} analysis and provide recommendations"
        expected_output = f"Comprehensive {role.title.lower()} report"
    
    task = NuiFloTask(
        task_name=f"{role.title} Analysis",
        description=description,
        expected_output=expected_output,
        role_id=role.id,
        team_execution_id=inputs.get("team_execution_id")
    )
    
    return task
```

##### Template-Based Tasks
```python
TASK_TEMPLATES = {
    "market_analysis": {
        "description": "Analyze the market for {product} targeting {audience}",
        "expected_output": "Comprehensive market analysis with size, trends, and opportunities"
    },
    "technical_design": {
        "description": "Design technical architecture for {project} with {requirements}",
        "expected_output": "Technical design document with architecture diagrams"
    },
    "content_strategy": {
        "description": "Develop content strategy for {campaign} reaching {audience}",
        "expected_output": "Content strategy with calendar and distribution plan"
    }
}

def create_task_from_template(template_name: str, role: Role, **params) -> NuiFloTask:
    """Create task from predefined template."""
    template = TASK_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown task template: {template_name}")
    
    description = template["description"].format(**params)
    expected_output = template["expected_output"].format(**params)
    
    return NuiFloTask(
        task_name=f"{role.title} - {template_name.title()}",
        description=description,
        expected_output=expected_output,
        role_id=role.id
    )
```

### Enhanced Crew Class (`NuiFloCrew`)

#### Overview
Extends CrewAI's Crew with team execution tracking and cost monitoring.

```python
class NuiFloCrew(Crew):
    """Enhanced Crew that extends CrewAI's Crew with team execution tracking."""
    
    def __init__(
        self,
        team_model: Team,
        execution_inputs: Dict[str, Any],
        **kwargs
    ):
        self.team_model = team_model
        self.execution_inputs = execution_inputs
        
        # Create execution record
        self.team_execution = self._create_execution_record()
        
        # Generate agents and tasks from team model
        agents, tasks = self._create_agents_and_tasks()
        
        super().__init__(
            agents=agents,
            tasks=tasks,
            verbose=True,
            **kwargs
        )
    
    def _create_agents_and_tasks(self) -> Tuple[List[NuiFloAgent], List[NuiFloTask]]:
        """Create agents and tasks from team roles."""
        agents = []
        tasks = []
        
        for role in self.team_model.roles:
            if role.is_active:
                # Create agent
                agent = NuiFloAgent(
                    role_model=role,
                    team_execution_id=self.team_execution.id
                )
                agents.append(agent)
                
                # Create task for agent
                task = create_task_from_role(role, self.execution_inputs)
                task.agent = agent
                tasks.append(task)
        
        return agents, tasks
```

#### Execution Methods

##### `kickoff_with_tracking()`
Enhanced execution with comprehensive tracking:

```python
async def kickoff_with_tracking(self) -> Dict[str, Any]:
    """Execute crew with full tracking and cost monitoring."""
    start_time = datetime.utcnow()
    
    try:
        # Update execution status
        self.team_execution.status = TeamStatus.RUNNING.value
        self.team_execution.started_at = start_time
        db.commit()
        
        # Track individual agent executions
        for agent in self.agents:
            agent.track_execution_start()
        
        # Execute crew
        result = self.kickoff()
        
        # Track completion
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Collect metrics from agents
        total_tokens = sum(agent.execution_metrics["tokens_used"] for agent in self.agents)
        total_cost = sum(agent.execution_metrics["cost"] for agent in self.agents)
        
        # Update execution record
        self.team_execution.status = TeamStatus.COMPLETED.value
        self.team_execution.result = str(result)
        self.team_execution.tokens_used = total_tokens
        self.team_execution.cost = total_cost
        self.team_execution.duration_seconds = Decimal(str(duration))
        self.team_execution.completed_at = end_time
        
        # Update team spending
        self.team_model.current_spend += total_cost
        self.team_model.last_executed_at = end_time
        
        db.commit()
        
        return {
            "result": str(result),
            "success": True,
            "error": None,
            "metrics": {
                "execution_time_seconds": duration,
                "total_tokens_used": total_tokens,
                "total_cost": float(total_cost),
                "tasks_completed": len(self.tasks),
                "agents_involved": len(self.agents)
            },
            "task_results": [
                {
                    "task_name": task.task_name,
                    "agent_role": task.agent.role_model.title,
                    "tokens_used": task.agent.execution_metrics["tokens_used"],
                    "cost": float(task.agent.execution_metrics["cost"]),
                    "duration_seconds": (
                        task.agent.execution_metrics["end_time"] - 
                        task.agent.execution_metrics["start_time"]
                    ).total_seconds() if task.agent.execution_metrics["start_time"] else 0,
                    "success": True
                }
                for task in self.tasks
            ]
        }
        
    except Exception as e:
        # Handle execution failure
        self.team_execution.status = TeamStatus.FAILED.value
        self.team_execution.error_message = str(e)
        self.team_execution.completed_at = datetime.utcnow()
        
        db.commit()
        
        logger.error("Crew execution failed", 
                    team_id=self.team_model.id,
                    error=str(e),
                    exc_info=True)
        
        return {
            "result": None,
            "success": False,
            "error": str(e),
            "metrics": {},
            "task_results": []
        }
```

---

## 🔄 Workflow Execution

### Team Execution Pipeline

#### High-Level Flow
```
1. Team Creation/Selection
   ↓
2. Input Validation & Processing
   ↓  
3. Agent & Task Generation
   ↓
4. LLM Routing & Selection
   ↓
5. Crew Execution
   ↓
6. Result Processing & Storage
   ↓
7. Cost Tracking & Budget Updates
```

#### Detailed Execution Process

##### Step 1: Team Preparation
```python
async def prepare_team_execution(
    team_id: int,
    execution_inputs: Dict[str, Any],
    execution_config: Dict[str, Any]
) -> Tuple[Team, TeamExecution]:
    """Prepare team for execution with validation."""
    
    # Get team with roles
    team = db.query(Team).options(
        selectinload(Team.roles)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(404, "Team not found")
    
    # Validate team state
    if team.status == TeamStatus.RUNNING:
        raise HTTPException(400, "Team is already running")
    
    # Check budget
    remaining_budget = team.monthly_budget - team.current_spend
    if remaining_budget <= 0:
        raise HTTPException(400, "Monthly budget exceeded")
    
    # Validate active roles
    active_roles = [r for r in team.roles if r.is_active]
    if not active_roles:
        raise HTTPException(400, "Team has no active roles")
    
    # Create execution record
    team_execution = TeamExecution(
        team_id=team.id,
        status=TeamStatus.RUNNING.value,
        execution_metadata={
            "inputs": execution_inputs,
            "config": execution_config,
            "remaining_budget": float(remaining_budget)
        }
    )
    db.add(team_execution)
    db.flush()
    
    return team, team_execution
```

##### Step 2: Agent Generation
```python
def generate_agents_from_team(
    team: Team,
    team_execution_id: int,
    execution_config: Dict[str, Any]
) -> List[NuiFloAgent]:
    """Generate NuiFlo agents from team roles."""
    
    agents = []
    
    for role in team.roles:
        if not role.is_active:
            continue
        
        # Create enhanced agent with role configuration
        agent = NuiFloAgent(
            role_model=role,
            team_execution_id=team_execution_id,
            
            # Override with execution config if provided
            max_iter=execution_config.get("max_iterations", 5),
            max_execution_time=execution_config.get("timeout_minutes", 30) * 60,
            allow_delegation=execution_config.get("allow_delegation", False)
        )
        
        agents.append(agent)
        
        logger.info("Generated agent from role",
                   role_id=role.id,
                   role_title=role.title,
                   llm_model=role.llm_model,
                   team_execution_id=team_execution_id)
    
    return agents
```

##### Step 3: Task Generation
```python
def generate_tasks_from_inputs(
    agents: List[NuiFloAgent],
    execution_inputs: Dict[str, Any],
    team_execution_id: int
) -> List[NuiFloTask]:
    """Generate tasks based on agents and execution inputs."""
    
    tasks = []
    
    # Base context for all tasks
    base_context = {
        "project_description": execution_inputs.get("project_description", ""),
        "timeline": execution_inputs.get("timeline", ""),
        "budget": execution_inputs.get("budget", 0),
        "target_audience": execution_inputs.get("target_audience", ""),
        "requirements": execution_inputs.get("requirements", [])
    }
    
    for agent in agents:
        role_title = agent.role_model.title.lower()
        
        # Generate role-specific task
        if "manager" in role_title or "strategist" in role_title:
            task = NuiFloTask(
                task_name=f"{agent.role_model.title} Strategy",
                description=f"""
                Develop a comprehensive strategy for: {base_context['project_description']}
                
                Timeline: {base_context['timeline']}
                Budget: ${base_context['budget']:,}
                Target Audience: {base_context['target_audience']}
                
                Provide strategic analysis, recommendations, and action plans.
                """,
                expected_output="Strategic analysis with actionable recommendations",
                role_id=agent.role_model.id,
                team_execution_id=team_execution_id,
                agent=agent
            )
            
        elif "developer" in role_title or "engineer" in role_title:
            task = NuiFloTask(
                task_name=f"{agent.role_model.title} Technical Design",
                description=f"""
                Design technical solution for: {base_context['project_description']}
                
                Requirements: {', '.join(base_context['requirements']) if base_context['requirements'] else 'To be determined'}
                Timeline: {base_context['timeline']}
                
                Provide technical architecture, implementation plan, and technology recommendations.
                """,
                expected_output="Technical design document with implementation roadmap",
                role_id=agent.role_model.id,
                team_execution_id=team_execution_id,
                agent=agent
            )
            
        elif "analyst" in role_title:
            task = NuiFloTask(
                task_name=f"{agent.role_model.title} Analysis",
                description=f"""
                Analyze market and requirements for: {base_context['project_description']}
                
                Target Audience: {base_context['target_audience']}
                Budget: ${base_context['budget']:,}
                
                Provide market analysis, competitive landscape, and feasibility assessment.
                """,
                expected_output="Comprehensive analysis report with insights and recommendations",
                role_id=agent.role_model.id,
                team_execution_id=team_execution_id,
                agent=agent
            )
            
        else:
            # Generic task for other roles
            task = NuiFloTask(
                task_name=f"{agent.role_model.title} Contribution",
                description=f"""
                Contribute your {agent.role_model.title.lower()} expertise to: {base_context['project_description']}
                
                Timeline: {base_context['timeline']}
                Target Audience: {base_context['target_audience']}
                
                Provide insights, recommendations, and deliverables relevant to your role.
                """,
                expected_output=f"Professional {agent.role_model.title.lower()} recommendations and deliverables",
                role_id=agent.role_model.id,
                team_execution_id=team_execution_id,
                agent=agent
            )
        
        tasks.append(task)
    
    return tasks
```

##### Step 4: Crew Execution
```python
async def execute_crew_with_monitoring(
    team: Team,
    agents: List[NuiFloAgent],
    tasks: List[NuiFloTask],
    execution_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute crew with real-time monitoring."""
    
    # Create crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,  # or hierarchical based on config
        verbose=execution_config.get("verbose", True)
    )
    
    # Monitor execution
    start_time = time.time()
    
    try:
        # Execute with timeout
        timeout = execution_config.get("timeout_minutes", 30) * 60
        result = await asyncio.wait_for(
            asyncio.to_thread(crew.kickoff),
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        
        # Collect metrics
        total_tokens = sum(
            agent.execution_metrics.get("tokens_used", 0) 
            for agent in agents
        )
        total_cost = sum(
            agent.execution_metrics.get("cost", Decimal("0.00")) 
            for agent in agents
        )
        
        return {
            "success": True,
            "result": str(result),
            "execution_time_seconds": execution_time,
            "total_tokens_used": total_tokens,
            "total_cost": float(total_cost),
            "tasks_completed": len(tasks),
            "agents_involved": len(agents)
        }
        
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": f"Execution timed out after {timeout} seconds",
            "execution_time_seconds": time.time() - start_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time_seconds": time.time() - start_time
        }
```

### Process Types

#### Sequential Process
Default execution where tasks are completed one after another:

```python
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

# Execution order:
# Task 1 (Agent 1) → Task 2 (Agent 2) → Task 3 (Agent 3)
```

#### Hierarchical Process
Manager-subordinate structure with delegation:

```python
# Identify manager agent (usually first or highest expertise)
manager_agent = max(agents, key=lambda a: a.role_model.expertise.value)

crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.hierarchical,
    manager_llm=manager_agent.llm,
    verbose=True
)

# Manager coordinates and delegates tasks to other agents
```

#### Custom Process
NuiFlo-specific execution patterns:

```python
class NuiFloProcess:
    """Custom execution process for NuiFlo crews."""
    
    @staticmethod
    async def collaborative_process(crew: NuiFloCrew) -> str:
        """Execute tasks with collaboration between agents."""
        
        results = []
        shared_context = {}
        
        for task in crew.tasks:
            # Add previous results to context
            task.context = shared_context
            
            # Execute task
            result = await task.execute()
            results.append(result)
            
            # Update shared context
            shared_context[task.agent.role_model.title] = result
        
        # Final synthesis by most senior agent
        senior_agent = max(crew.agents, key=lambda a: a.role_model.expertise.value)
        synthesis = await senior_agent.synthesize_results(results)
        
        return synthesis
```

---

## 🧠 Intelligent LLM Integration

### Hybrid Crew System

#### Overview
The hybrid crew system integrates the Intelligent LLM Router with CrewAI to provide cost-optimized, performance-aware execution.

```python
from workforce_api.services.hybrid_crew_extensions import create_hybrid_crew_from_team

async def create_hybrid_crew_from_team(
    team: Team,
    execution_inputs: Dict[str, Any],
    quality_preference: str = "balanced",
    max_budget_per_task: Optional[float] = None
) -> Dict[str, Any]:
    """Create crew with intelligent LLM routing."""
```

#### Quality Preferences

| Preference | Strategy | Use Cases | Cost Impact |
|------------|----------|-----------|-------------|
| `fast` | Ollama first, minimal commercial LLM | Rapid prototyping, simple tasks | Minimal |
| `balanced` | Smart routing based on complexity | General purpose, mixed complexity | Medium |
| `premium` | GPT-4/Claude for complex reasoning | Critical projects, high accuracy needed | High |
| `cost_optimized` | Maximum Ollama usage | Budget-constrained projects | Minimal |

#### Implementation

##### Hybrid Agent Creation
```python
class HybridNuiFloAgent(NuiFloAgent):
    """Agent with intelligent LLM routing capabilities."""
    
    def __init__(
        self,
        role_model: Role,
        llm_router: IntelligentLLMRouter,
        quality_preference: str = "balanced",
        max_budget: Optional[float] = None,
        **kwargs
    ):
        self.llm_router = llm_router
        self.quality_preference = quality_preference
        self.max_budget = max_budget
        
        # Initialize base agent
        super().__init__(role_model, **kwargs)
    
    async def execute_task_with_routing(
        self,
        task_prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute task with intelligent LLM routing."""
        
        # Get routing decision
        routing_decision = self.llm_router.route_request(
            prompt=task_prompt,
            context=context,
            quality_preference=self.quality_preference,
            budget_limit=self.max_budget
        )
        
        logger.info("LLM routing decision",
                   role=self.role_model.title,
                   provider=routing_decision.provider.value,
                   estimated_cost=float(routing_decision.estimated_cost),
                   reasoning=routing_decision.reasoning)
        
        # Execute with selected provider
        result = await self.llm_router.execute_request(
            routing_decision,
            task_prompt
        )
        
        # Track execution metrics
        self.track_execution_end(
            tokens_used=result.actual_tokens,
            cost=result.actual_cost
        )
        
        return {
            "content": result.content,
            "provider": result.provider.value,
            "tokens_used": result.actual_tokens,
            "cost": result.actual_cost,
            "duration": result.duration_seconds,
            "routing_reasoning": routing_decision.reasoning,
            "success": result.success,
            "error": result.error
        }
```

##### Task Complexity Analysis
```python
def analyze_task_complexity(task: NuiFloTask, role: Role) -> ComplexityLevel:
    """Analyze task complexity for routing decisions."""
    
    factors = []
    
    # Task description analysis
    description_words = len(task.description.split())
    if description_words > 200:
        factors.append("long_description")
    
    # Required output complexity
    output_words = len(task.expected_output.split())
    if output_words > 50:
        factors.append("complex_output")
    
    # Role expertise consideration
    if role.expertise in [ExpertiseLevel.SENIOR, ExpertiseLevel.EXPERT]:
        factors.append("high_expertise")
    
    # Keyword analysis
    complex_keywords = [
        "analyze", "strategy", "comprehensive", "detailed",
        "architecture", "design", "plan", "roadmap"
    ]
    
    if any(keyword in task.description.lower() for keyword in complex_keywords):
        factors.append("complex_keywords")
    
    # Determine complexity level
    if len(factors) >= 3:
        return ComplexityLevel.COMPLEX
    elif len(factors) >= 2:
        return ComplexityLevel.MEDIUM
    else:
        return ComplexityLevel.SIMPLE
```

##### Budget-Aware Execution
```python
class BudgetAwareExecution:
    """Manages budget constraints during execution."""
    
    def __init__(self, team: Team, max_budget_per_task: Optional[float] = None):
        self.team = team
        self.max_budget_per_task = max_budget_per_task
        self.current_execution_cost = Decimal("0.00")
        
    def check_budget_before_task(self, estimated_cost: Decimal) -> bool:
        """Check if task execution is within budget."""
        
        # Check team monthly budget
        remaining_budget = self.team.monthly_budget - self.team.current_spend
        if remaining_budget <= 0:
            raise HTTPException(400, "Team monthly budget exceeded")
        
        # Check execution budget
        if self.current_execution_cost + estimated_cost > remaining_budget:
            raise HTTPException(400, f"Execution would exceed remaining budget: ${remaining_budget}")
        
        # Check per-task budget
        if self.max_budget_per_task and estimated_cost > Decimal(str(self.max_budget_per_task)):
            logger.warning("Task cost exceeds per-task budget, using cost-optimized routing",
                          estimated_cost=float(estimated_cost),
                          max_budget=self.max_budget_per_task)
            return False
        
        return True
    
    def record_task_cost(self, actual_cost: Decimal):
        """Record actual task cost."""
        self.current_execution_cost += actual_cost
        
        # Warning if approaching budget limit
        remaining = self.team.monthly_budget - self.team.current_spend - self.current_execution_cost
        if remaining < (self.team.monthly_budget * 0.1):  # Less than 10% remaining
            logger.warning("Approaching budget limit",
                          team_id=self.team.id,
                          remaining_budget=float(remaining),
                          utilization=(self.team.current_spend + self.current_execution_cost) / self.team.monthly_budget * 100)
```

---

## 🚀 Advanced Usage Patterns

### Multi-Team Orchestration

#### Team Collaboration
```python
async def orchestrate_multiple_teams(
    team_ids: List[int],
    shared_inputs: Dict[str, Any],
    coordination_strategy: str = "sequential"
) -> Dict[str, Any]:
    """Orchestrate execution across multiple teams."""
    
    teams = [TeamService.get_team_with_roles(team_id) for team_id in team_ids]
    results = {}
    shared_context = {}
    
    if coordination_strategy == "sequential":
        # Execute teams one after another
        for team in teams:
            # Add previous results to context
            team_inputs = {**shared_inputs, "previous_results": shared_context}
            
            result = await create_hybrid_crew_from_team(
                team=team,
                execution_inputs=team_inputs,
                quality_preference="balanced"
            )
            
            results[team.name] = result
            shared_context[team.name] = result.get("result", "")
    
    elif coordination_strategy == "parallel":
        # Execute teams in parallel
        tasks = [
            create_hybrid_crew_from_team(
                team=team,
                execution_inputs=shared_inputs,
                quality_preference="balanced"
            )
            for team in teams
        ]
        
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for team, result in zip(teams, parallel_results):
            if isinstance(result, Exception):
                results[team.name] = {"success": False, "error": str(result)}
            else:
                results[team.name] = result
    
    # Synthesize final result
    synthesis_prompt = f"""
    Synthesize the results from multiple AI teams working on: {shared_inputs.get('project_description', 'the project')}
    
    Team Results:
    {chr(10).join([f"**{name}**: {result.get('result', 'No result')}" for name, result in results.items()])}
    
    Provide a unified, comprehensive summary and actionable recommendations.
    """
    
    # Use best available team for synthesis
    synthesis_team = max(teams, key=lambda t: len([r for r in t.roles if r.expertise in [ExpertiseLevel.SENIOR, ExpertiseLevel.EXPERT]]))
    
    synthesis_result = await create_hybrid_crew_from_team(
        team=synthesis_team,
        execution_inputs={"project_description": synthesis_prompt},
        quality_preference="premium"
    )
    
    return {
        "individual_results": results,
        "synthesis": synthesis_result.get("result", ""),
        "total_cost": sum(r.get("metrics", {}).get("total_cost", 0) for r in results.values()),
        "execution_summary": {
            "teams_involved": len(teams),
            "total_agents": sum(len(team.roles) for team in teams),
            "coordination_strategy": coordination_strategy
        }
    }
```

### Iterative Refinement

#### Multi-Pass Execution
```python
class IterativeTeamExecution:
    """Manages iterative refinement of team outputs."""
    
    def __init__(self, team: Team, max_iterations: int = 3):
        self.team = team
        self.max_iterations = max_iterations
        self.iteration_results = []
    
    async def execute_with_refinement(
        self,
        initial_inputs: Dict[str, Any],
        quality_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """Execute team with iterative refinement."""
        
        current_inputs = initial_inputs.copy()
        
        for iteration in range(self.max_iterations):
            logger.info(f"Starting iteration {iteration + 1}/{self.max_iterations}",
                       team_id=self.team.id)
            
            # Execute team
            result = await create_hybrid_crew_from_team(
                team=self.team,
                execution_inputs=current_inputs,
                quality_preference="balanced" if iteration == 0 else "premium"
            )
            
            self.iteration_results.append(result)
            
            if not result["success"]:
                logger.error(f"Iteration {iteration + 1} failed", error=result.get("error"))
                break
            
            # Evaluate quality
            quality_score = await self._evaluate_result_quality(result["result"])
            
            logger.info(f"Iteration {iteration + 1} quality score: {quality_score}")
            
            if quality_score >= quality_threshold:
                logger.info("Quality threshold met, stopping iterations")
                break
            
            # Prepare inputs for next iteration
            current_inputs = self._prepare_refinement_inputs(
                original_inputs=initial_inputs,
                previous_result=result["result"],
                quality_feedback=await self._get_quality_feedback(result["result"])
            )
        
        # Return best result
        best_result = max(self.iteration_results, key=lambda r: r.get("quality_score", 0))
        
        return {
            **best_result,
            "iteration_count": len(self.iteration_results),
            "quality_improvement": self._calculate_quality_improvement(),
            "total_cost": sum(r.get("metrics", {}).get("total_cost", 0) for r in self.iteration_results)
        }
    
    async def _evaluate_result_quality(self, result: str) -> float:
        """Evaluate quality of team result."""
        
        # Use LLM to evaluate quality
        evaluation_prompt = f"""
        Evaluate the quality of this AI team result on a scale of 0.0 to 1.0:
        
        Result:
        {result}
        
        Consider:
        - Completeness and thoroughness
        - Clarity and organization
        - Actionability of recommendations
        - Professional quality
        
        Return only a number between 0.0 and 1.0.
        """
        
        # Use premium model for evaluation
        router = IntelligentLLMRouter()
        decision = router.route_request(
            prompt=evaluation_prompt,
            quality_preference="premium"
        )
        
        eval_result = await router.execute_request(decision, evaluation_prompt)
        
        try:
            score = float(eval_result.content.strip())
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except ValueError:
            logger.warning("Could not parse quality score, defaulting to 0.5")
            return 0.5
```

### Dynamic Team Composition

#### Adaptive Role Selection
```python
class AdaptiveTeamBuilder:
    """Builds teams dynamically based on project requirements."""
    
    def __init__(self):
        self.role_templates = self._load_role_templates()
    
    def analyze_project_requirements(self, project_description: str) -> List[str]:
        """Analyze project to determine required roles."""
        
        # Use LLM to analyze requirements
        analysis_prompt = f"""
        Analyze this project description and identify the key roles needed:
        
        Project: {project_description}
        
        Consider what types of expertise would be needed. Return a list of role titles, one per line.
        Focus on essential roles only (maximum 5).
        """
        
        # Use fast model for analysis
        router = IntelligentLLMRouter()
        decision = router.route_request(
            prompt=analysis_prompt,
            quality_preference="fast"
        )
        
        result = router.execute_request(decision, analysis_prompt)
        
        # Parse roles from result
        roles = [line.strip() for line in result.content.split('\n') if line.strip()]
        return roles[:5]  # Limit to 5 roles
    
    async def build_adaptive_team(
        self,
        owner_id: str,
        project_description: str,
        budget: Decimal,
        expertise_level: str = "intermediate"
    ) -> Team:
        """Build team with roles adapted to project needs."""
        
        # Analyze requirements
        required_roles = self.analyze_project_requirements(project_description)
        
        # Create team
        team = TeamService.create_team(
            name=f"Adaptive Team - {project_description[:30]}...",
            owner_id=owner_id,
            monthly_budget=budget,
            description=f"Dynamically composed team for: {project_description}"
        )
        
        # Create roles based on analysis
        for role_title in required_roles:
            role_config = self._generate_role_config(role_title, expertise_level)
            
            role = Role(
                team_id=team.id,
                title=role_title,
                description=role_config["description"],
                expertise=ExpertiseLevel[expertise_level.upper()],
                llm_model=role_config["llm_model"],
                agent_config=role_config["agent_config"]
            )
            
            db.add(role)
        
        db.commit()
        
        logger.info("Built adaptive team",
                   team_id=team.id,
                   roles=required_roles,
                   project=project_description[:50])
        
        return team
    
    def _generate_role_config(self, role_title: str, expertise_level: str) -> Dict[str, Any]:
        """Generate configuration for a role."""
        
        # Default configurations based on role type
        if "manager" in role_title.lower() or "lead" in role_title.lower():
            return {
                "description": f"Strategic {role_title.lower()} with leadership experience",
                "llm_model": "gpt-4",
                "agent_config": {
                    "backstory": f"Experienced {role_title.lower()} with proven track record",
                    "goals": ["Provide strategic direction", "Coordinate team efforts"],
                    "allow_delegation": True
                }
            }
        elif "developer" in role_title.lower() or "engineer" in role_title.lower():
            return {
                "description": f"Technical {role_title.lower()} with implementation expertise",
                "llm_model": "deepseek-coder:6.7b" if expertise_level == "intermediate" else "gpt-4",
                "agent_config": {
                    "backstory": f"Skilled {role_title.lower()} with hands-on experience",
                    "goals": ["Design technical solutions", "Provide implementation guidance"],
                    "tools": ["code_analysis", "architecture_design"]
                }
            }
        else:
            return {
                "description": f"Professional {role_title.lower()} with domain expertise",
                "llm_model": "gpt-3.5-turbo",
                "agent_config": {
                    "backstory": f"Expert {role_title.lower()} with specialized knowledge",
                    "goals": ["Provide domain expertise", "Deliver professional insights"]
                }
            }
```

---

## 📊 Performance Optimization

### Execution Optimization

#### Parallel Task Execution
```python
async def execute_parallel_tasks(
    agents: List[NuiFloAgent],
    tasks: List[NuiFloTask]
) -> List[Dict[str, Any]]:
    """Execute tasks in parallel where possible."""
    
    # Group tasks by dependencies
    independent_tasks = []
    dependent_tasks = []
    
    for task in tasks:
        if hasattr(task, 'dependencies') and task.dependencies:
            dependent_tasks.append(task)
        else:
            independent_tasks.append(task)
    
    results = []
    
    # Execute independent tasks in parallel
    if independent_tasks:
        parallel_futures = [
            execute_single_task(task)
            for task in independent_tasks
        ]
        
        parallel_results = await asyncio.gather(*parallel_futures, return_exceptions=True)
        
        for task, result in zip(independent_tasks, parallel_results):
            if isinstance(result, Exception):
                results.append({
                    "task_name": task.task_name,
                    "success": False,
                    "error": str(result)
                })
            else:
                results.append(result)
    
    # Execute dependent tasks sequentially
    for task in dependent_tasks:
        result = await execute_single_task(task)
        results.append(result)
    
    return results

async def execute_single_task(task: NuiFloTask) -> Dict[str, Any]:
    """Execute a single task with metrics tracking."""
    start_time = time.time()
    
    try:
        # Track execution start
        task.agent.track_execution_start()
        
        # Execute task
        result = await task.execute()
        
        duration = time.time() - start_time
        
        # Track completion
        task.agent.track_execution_end()
        
        return {
            "task_name": task.task_name,
            "agent_role": task.agent.role_model.title,
            "result": str(result),
            "duration_seconds": duration,
            "tokens_used": task.agent.execution_metrics.get("tokens_used", 0),
            "cost": float(task.agent.execution_metrics.get("cost", 0)),
            "success": True
        }
        
    except Exception as e:
        return {
            "task_name": task.task_name,
            "agent_role": task.agent.role_model.title,
            "error": str(e),
            "duration_seconds": time.time() - start_time,
            "success": False
        }
```

#### Caching and Memoization
```python
from functools import lru_cache
import hashlib

class ExecutionCache:
    """Caches execution results for similar inputs."""
    
    def __init__(self, max_cache_size: int = 100):
        self.cache = {}
        self.max_cache_size = max_cache_size
    
    def _generate_cache_key(
        self,
        team_id: int,
        execution_inputs: Dict[str, Any],
        quality_preference: str
    ) -> str:
        """Generate cache key for execution."""
        
        # Create deterministic hash of inputs
        cache_data = {
            "team_id": team_id,
            "inputs": execution_inputs,
            "quality": quality_preference
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_result(
        self,
        team_id: int,
        execution_inputs: Dict[str, Any],
        quality_preference: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached execution result if available."""
        
        cache_key = self._generate_cache_key(team_id, execution_inputs, quality_preference)
        
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            
            # Check if cache is still valid (e.g., within 1 hour)
            cache_age = time.time() - cached_result["cached_at"]
            if cache_age < 3600:  # 1 hour
                logger.info("Using cached execution result", cache_key=cache_key)
                return cached_result["result"]
        
        return None
    
    def cache_result(
        self,
        team_id: int,
        execution_inputs: Dict[str, Any],
        quality_preference: str,
        result: Dict[str, Any]
    ):
        """Cache execution result."""
        
        cache_key = self._generate_cache_key(team_id, execution_inputs, quality_preference)
        
        # Manage cache size
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["cached_at"])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            "result": result,
            "cached_at": time.time()
        }
        
        logger.info("Cached execution result", cache_key=cache_key)

# Global cache instance
execution_cache = ExecutionCache()
```

#### Resource Management
```python
class ResourceManager:
    """Manages system resources during execution."""
    
    def __init__(self, max_concurrent_executions: int = 5):
        self.max_concurrent_executions = max_concurrent_executions
        self.active_executions = 0
        self.execution_queue = asyncio.Queue()
        self.execution_semaphore = asyncio.Semaphore(max_concurrent_executions)
    
    async def execute_with_resource_management(
        self,
        execution_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with resource management."""
        
        async with self.execution_semaphore:
            self.active_executions += 1
            
            try:
                logger.info("Starting execution",
                           active_executions=self.active_executions,
                           max_concurrent=self.max_concurrent_executions)
                
                result = await execution_func(*args, **kwargs)
                
                return result
                
            finally:
                self.active_executions -= 1
                logger.info("Execution completed",
                           active_executions=self.active_executions)
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource utilization."""
        return {
            "active_executions": self.active_executions,
            "max_concurrent": self.max_concurrent_executions,
            "available_slots": self.max_concurrent_executions - self.active_executions,
            "queue_size": self.execution_queue.qsize()
        }

# Global resource manager
resource_manager = ResourceManager(max_concurrent_executions=3)
```

### Complete Integration Example

#### Production-Ready Execution
```python
async def production_team_execution(
    team_id: int,
    execution_inputs: Dict[str, Any],
    execution_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Production-ready team execution with all optimizations."""
    
    # Default configuration
    config = {
        "quality_preference": "balanced",
        "max_budget_per_task": None,
        "use_cache": True,
        "enable_parallel": True,
        "max_iterations": 3,
        "timeout_minutes": 30,
        **execution_config or {}
    }
    
    # Check cache first
    if config["use_cache"]:
        cached_result = execution_cache.get_cached_result(
            team_id=team_id,
            execution_inputs=execution_inputs,
            quality_preference=config["quality_preference"]
        )
        
        if cached_result:
            return {
                **cached_result,
                "cached": True,
                "cache_hit": True
            }
    
    # Execute with resource management
    result = await resource_manager.execute_with_resource_management(
        _execute_team_internal,
        team_id=team_id,
        execution_inputs=execution_inputs,
        config=config
    )
    
    # Cache successful results
    if config["use_cache"] and result.get("success"):
        execution_cache.cache_result(
            team_id=team_id,
            execution_inputs=execution_inputs,
            quality_preference=config["quality_preference"],
            result=result
        )
    
    return result

async def _execute_team_internal(
    team_id: int,
    execution_inputs: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Internal execution with hybrid crew system."""
    
    # Get team
    team = TeamService.get_team_with_roles(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    
    # Execute with hybrid system
    result = await create_hybrid_crew_from_team(
        team=team,
        execution_inputs=execution_inputs,
        quality_preference=config["quality_preference"],
        max_budget_per_task=config["max_budget_per_task"]
    )
    
    # Add execution metadata
    result["execution_config"] = config
    result["team_info"] = {
        "id": team.id,
        "name": team.name,
        "role_count": len(team.roles),
        "active_roles": len([r for r in team.roles if r.is_active])
    }
    
    return result
```

---

**This completes the comprehensive CrewAI integration documentation. The system provides a robust, scalable platform for orchestrating AI agent teams with intelligent routing, cost optimization, and performance monitoring.**