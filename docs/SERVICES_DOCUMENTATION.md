# NuiFlo WorkForce - Services Documentation

## 🏗️ Overview

This document provides comprehensive documentation for all business logic services in the NuiFlo WorkForce platform, including team management, CrewAI integration, and execution tracking.

## 📋 Table of Contents

1. [Team Service](#-team-service)
2. [CrewAI Extensions](#-crewai-extensions)
3. [Hybrid Crew Extensions](#-hybrid-crew-extensions)
4. [Service Integration Patterns](#-service-integration-patterns)

---

## 👥 Team Service

### Overview (`workforce_api.services.team_service`)

The TeamService class handles all business logic related to team management, including creation, modification, execution tracking, and resource management.

#### Key Features
- **Team lifecycle management** (create, read, update, delete)
- **Role management** within teams
- **Budget tracking** and spend monitoring
- **Team status management** 
- **Performance metrics** calculation
- **Session management** with optional database session injection

#### Class Structure

```python
class TeamService:
    """Enhanced team management service with intelligent routing capabilities"""
    
    # Static methods for stateless operations
    @staticmethod
    def create_team(...)
    
    @staticmethod
    def get_team(...)
    
    @staticmethod
    def update_team(...)
    
    # Instance methods would be used for stateful operations
```

### Core Methods

#### `create_team()`

Creates a new team with roles and initializes budget tracking.

```python
@staticmethod
def create_team(
    name: str,
    owner_id: str,  # UUID from Supabase
    monthly_budget: Decimal,
    description: Optional[str] = None,
    roles_data: Optional[List[Dict[str, Any]]] = None,
    session: Optional[Session] = None
) -> Team:
```

**Parameters:**
- `name` (str): Team name (1-100 characters)
- `owner_id` (str): Supabase user UUID
- `monthly_budget` (Decimal): Monthly budget in USD
- `description` (str, optional): Team description
- `roles_data` (List[Dict], optional): List of role configurations
- `session` (Session, optional): Database session for transaction management

**Returns:** Created `Team` object with relationships loaded

**Usage Example:**
```python
from workforce_api.services import TeamService
from decimal import Decimal

# Create team with roles
team = TeamService.create_team(
    name="Marketing Team",
    owner_id="550e8400-e29b-41d4-a716-446655440000",
    monthly_budget=Decimal("500.00"),
    description="AI team for marketing campaigns",
    roles_data=[
        {
            "title": "Content Strategist",
            "description": "Creates content strategies and plans",
            "expertise": "SENIOR",
            "llm_model": "gpt-4",
            "backstory": "Expert marketing strategist with 10+ years experience",
            "goals": ["Create compelling content", "Analyze market trends"],
            "tools": ["market_research", "analytics"]
        },
        {
            "title": "Copywriter",
            "expertise": "INTERMEDIATE",
            "llm_model": "gpt-3.5-turbo",
            "is_active": True
        }
    ]
)

print(f"Created team: {team.name} with {len(team.roles)} roles")
```

**Role Data Structure:**
```python
{
    "title": str,                    # Required: Role title
    "description": str,              # Optional: Role description
    "expertise": ExpertiseLevel,     # Required: JUNIOR/INTERMEDIATE/SENIOR/EXPERT
    "llm_model": str,               # Required: Model identifier
    "llm_config": Dict[str, Any],   # Optional: Model configuration
    "agent_config": Dict[str, Any], # Optional: CrewAI agent configuration
    "is_active": bool,              # Optional: Default True
    "system_prompt": str,           # Optional: System prompt
    "backstory": str,               # Optional: Agent backstory
    "goals": List[str],             # Optional: Agent goals
    "tools": List[str]              # Optional: Available tools
}
```

#### `get_team()` and `get_team_with_roles()`

Retrieves team information with optional role loading.

```python
@staticmethod
def get_team(team_id: int, session: Optional[Session] = None) -> Optional[Team]:
    """Get team by ID without roles"""

@staticmethod  
def get_team_with_roles(team_id: int, session: Optional[Session] = None) -> Optional[Team]:
    """Get team by ID with roles eagerly loaded"""
```

**Usage Example:**
```python
# Basic team info
team = TeamService.get_team(team_id=123)
if team:
    print(f"Team: {team.name}, Budget: ${team.monthly_budget}")

# Team with roles loaded
team_with_roles = TeamService.get_team_with_roles(team_id=123)
if team_with_roles:
    print(f"Team has {len(team_with_roles.roles)} roles")
    for role in team_with_roles.roles:
        print(f"  - {role.title} ({role.expertise.value})")
```

#### `get_teams_by_owner()`

Retrieves all teams for a specific owner with pagination support.

```python
@staticmethod
def get_teams_by_owner(
    owner_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Optional[Session] = None
) -> List[Team]:
```

**Usage Example:**
```python
# Get user's teams
user_teams = TeamService.get_teams_by_owner(
    owner_id="550e8400-e29b-41d4-a716-446655440000",
    skip=0,
    limit=10
)

for team in user_teams:
    print(f"Team: {team.name} - Status: {team.status.value}")
```

#### `update_team()`

Updates team properties and manages role modifications.

```python
@staticmethod
def update_team(
    team_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    monthly_budget: Optional[Decimal] = None,
    session: Optional[Session] = None
) -> Optional[Team]:
```

**Usage Example:**
```python
# Update team budget and description
updated_team = TeamService.update_team(
    team_id=123,
    description="Updated marketing team with expanded scope",
    monthly_budget=Decimal("750.00")
)

if updated_team:
    print(f"Updated team: {updated_team.name}")
    print(f"New budget: ${updated_team.monthly_budget}")
```

#### `delete_team()`

Safely deletes a team and all associated data.

```python
@staticmethod
def delete_team(team_id: int, session: Optional[Session] = None) -> bool:
```

**Usage Example:**
```python
# Delete team
success = TeamService.delete_team(team_id=123)
if success:
    print("Team deleted successfully")
else:
    print("Team not found or deletion failed")
```

#### `update_team_spend()`

Updates team spending and tracks budget utilization.

```python
@staticmethod
def update_team_spend(
    team_id: int,
    cost: Decimal,
    session: Optional[Session] = None
) -> Optional[Team]:
```

**Usage Example:**
```python
from decimal import Decimal

# Record execution cost
team = TeamService.update_team_spend(
    team_id=123,
    cost=Decimal("15.75")
)

if team:
    utilization = (team.current_spend / team.monthly_budget) * 100
    print(f"Budget utilization: {utilization:.1f}%")
```

#### `get_team_status()`

Provides comprehensive team status and performance metrics.

```python
@staticmethod
def get_team_status(team_id: int, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
```

**Returns:**
```python
{
    "team_id": int,
    "name": str,
    "status": str,
    "monthly_budget": float,
    "current_spend": float,
    "budget_utilization": float,  # Percentage
    "last_executed_at": Optional[str],
    "role_count": int,
    "active_roles": int,
    "performance_metrics": {
        "total_executions": int,
        "successful_executions": int,
        "failed_executions": int,
        "average_duration_seconds": float,
        "total_tokens_used": int,
        "average_cost_per_execution": float
    }
}
```

**Usage Example:**
```python
# Get comprehensive team status
status = TeamService.get_team_status(team_id=123)
if status:
    print(f"Team: {status['name']}")
    print(f"Budget utilization: {status['budget_utilization']:.1f}%")
    print(f"Success rate: {status['performance_metrics']['successful_executions']} / {status['performance_metrics']['total_executions']}")
```

### Transaction Management

The TeamService supports both automatic and manual transaction management:

#### Automatic Session Management
```python
# Service handles session creation and cleanup
team = TeamService.create_team(
    name="Auto Session Team",
    owner_id="user-uuid",
    monthly_budget=Decimal("200.00")
)
```

#### Manual Session Management
```python
from workforce_api.core.database import SessionLocal

# Manual session for complex operations
with SessionLocal() as db:
    try:
        # Multiple operations in single transaction
        team = TeamService.create_team(
            name="Manual Session Team",
            owner_id="user-uuid", 
            monthly_budget=Decimal("300.00"),
            session=db
        )
        
        # Update team in same transaction
        updated_team = TeamService.update_team(
            team_id=team.id,
            description="Updated in same transaction",
            session=db
        )
        
        db.commit()
        print("All operations completed successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Transaction failed: {e}")
```

---

## 🤖 CrewAI Extensions

### Overview (`workforce_api.services.crew_extensions`)

The CrewAI Extensions provide enhanced Agent and Task classes that integrate with the NuiFlo database for tracking, metrics collection, and cost monitoring.

#### Key Features
- **Database-integrated agents** with execution tracking
- **Cost monitoring** and budget management
- **Performance metrics** collection
- **Error handling** and logging
- **Execution history** for audit trails

### Enhanced Agent Class

#### `NuiFloAgent`

Extends CrewAI's Agent class with database integration and execution tracking.

```python
class NuiFloAgent(Agent):
    """Enhanced Agent that extends CrewAI's Agent with database tracking."""
    
    def __init__(
        self,
        role_model: Role,
        team_execution_id: Optional[int] = None,
        **kwargs
    ):
```

**Parameters:**
- `role_model` (Role): Database Role model containing agent configuration
- `team_execution_id` (int, optional): Current team execution ID for tracking
- `**kwargs`: Additional CrewAI Agent parameters

**Automatic Configuration:**
The agent automatically configures itself from the Role model:

```python
# Agent properties derived from Role model
role = role_model.title                    # Agent role name
goal = f"Expert {expertise} level {title}" # Generated goal
backstory = f"You are a {expertise} level {title}..." # Generated backstory
llm = role_model.llm_model                 # LLM configuration
```

**Usage Example:**
```python
from workforce_api.services.crew_extensions import NuiFloAgent
from workforce_api.models import Role

# Get role from database
role = db.query(Role).filter(Role.id == 1).first()

# Create enhanced agent
agent = NuiFloAgent(
    role_model=role,
    team_execution_id=123,
    verbose=True,
    allow_delegation=False
)

print(f"Created agent: {agent.role}")
print(f"LLM Model: {agent.llm}")
```

#### Execution Tracking Methods

##### `track_execution_start()`
Starts execution tracking and logging.

```python
def track_execution_start(self):
    """Start tracking execution metrics."""
```

##### `track_execution_end()`
Ends tracking and updates metrics.

```python
def track_execution_end(self, tokens_used: int = 0, cost: Decimal = Decimal("0.00")):
    """End tracking and update metrics."""
```

**Usage Example:**
```python
# Manual tracking
agent.track_execution_start()

# Perform agent work
result = agent.execute_task(task)

# End tracking with metrics
agent.track_execution_end(
    tokens_used=1500,
    cost=Decimal("0.045")
)

print(f"Execution metrics: {agent.execution_metrics}")
```

### Enhanced Task Class

#### `NuiFloTask`

Extends CrewAI's Task class with database tracking and metrics collection.

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
```

**Parameters:**
- `task_name` (str): Descriptive name for the task
- `role_id` (int): Database ID of the role executing this task
- `team_execution_id` (int, optional): Team execution ID for tracking
- `**kwargs`: Additional CrewAI Task parameters

**Usage Example:**
```python
from workforce_api.services.crew_extensions import NuiFloTask

# Create enhanced task
task = NuiFloTask(
    task_name="Market Analysis",
    description="Analyze current market trends and competition",
    role_id=1,
    team_execution_id=123,
    expected_output="Comprehensive market analysis report"
)
```

### Enhanced Crew Class

#### `NuiFloCrew`

Extends CrewAI's Crew class with team execution tracking and cost monitoring.

```python
class NuiFloCrew(Crew):
    """Enhanced Crew that extends CrewAI's Crew with team execution tracking."""
    
    def __init__(
        self,
        team_model: Team,
        execution_inputs: Dict[str, Any],
        **kwargs
    ):
```

**Parameters:**
- `team_model` (Team): Database Team model with roles
- `execution_inputs` (Dict): Input parameters for execution
- `**kwargs**: Additional CrewAI Crew parameters

**Automatic Agent and Task Creation:**
The crew automatically creates NuiFloAgent and NuiFloTask instances from the team configuration:

```python
# Agents created from team roles
for role in team_model.roles:
    if role.is_active:
        agent = NuiFloAgent(role_model=role, team_execution_id=execution_id)
        agents.append(agent)

# Tasks created for each role
for agent in agents:
    task = NuiFloTask(
        task_name=f"{agent.role} Task",
        role_id=agent.role_model.id,
        team_execution_id=execution_id
    )
    tasks.append(task)
```

#### Execution Methods

##### `kickoff_with_tracking()`

Executes the crew with comprehensive tracking and error handling.

```python
async def kickoff_with_tracking(self) -> Dict[str, Any]:
    """Execute crew with full tracking and cost monitoring."""
```

**Returns:**
```python
{
    "result": str,              # Crew execution result
    "success": bool,            # Execution success status
    "error": Optional[str],     # Error message if failed
    "metrics": {
        "execution_time_seconds": float,
        "total_tokens_used": int,
        "total_cost": Decimal,
        "tasks_completed": int,
        "agents_involved": int
    },
    "task_results": [           # Individual task results
        {
            "task_name": str,
            "agent_role": str,
            "result": str,
            "tokens_used": int,
            "cost": Decimal,
            "duration_seconds": float,
            "success": bool
        }
    ]
}
```

**Usage Example:**
```python
from workforce_api.services.crew_extensions import NuiFloCrew

# Create and execute crew
crew = NuiFloCrew(
    team_model=team,
    execution_inputs={
        "project_description": "Build a mobile app",
        "timeline": "3 months",
        "budget": 50000
    },
    verbose=True,
    process=Process.sequential
)

# Execute with tracking
result = await crew.kickoff_with_tracking()

if result["success"]:
    print(f"Execution completed successfully")
    print(f"Total cost: ${result['metrics']['total_cost']}")
    print(f"Duration: {result['metrics']['execution_time_seconds']} seconds")
else:
    print(f"Execution failed: {result['error']}")
```

### Database Integration

#### Execution Record Creation

The CrewAI extensions automatically create database records for tracking:

```python
# TeamExecution record
team_execution = TeamExecution(
    team_id=team.id,
    status=TeamStatus.RUNNING,
    execution_metadata=execution_inputs,
    started_at=datetime.utcnow()
)

# TaskExecution records for each task
task_execution = TaskExecution(
    team_execution_id=team_execution.id,
    role_id=role.id,
    task_name=task_name,
    status=TeamStatus.RUNNING,
    started_at=datetime.utcnow()
)
```

#### Cost Tracking Integration

```python
# Update team spending
team.current_spend += total_cost

# Record individual task costs
task_execution.cost = task_cost
task_execution.tokens_used = tokens_used
task_execution.duration_seconds = duration

# Update team execution totals
team_execution.cost = sum(task.cost for task in task_executions)
team_execution.tokens_used = sum(task.tokens_used for task in task_executions)
```

---

## 🔄 Hybrid Crew Extensions

### Overview (`workforce_api.services.hybrid_crew_extensions`)

The Hybrid Crew Extensions integrate the Intelligent LLM Router with CrewAI to provide cost-optimized, performance-aware team execution.

#### Key Features
- **Intelligent LLM routing** for each agent
- **Cost optimization** across multiple providers
- **Automatic fallback** handling
- **Quality preference** management
- **Budget constraint** enforcement

### `create_hybrid_crew_from_team()`

Creates a hybrid crew with intelligent LLM routing capabilities.

```python
async def create_hybrid_crew_from_team(
    team: Team,
    execution_inputs: Dict[str, Any],
    quality_preference: str = "balanced",
    max_budget_per_task: Optional[float] = None
) -> Dict[str, Any]:
```

**Parameters:**
- `team` (Team): Database team model with roles
- `execution_inputs` (Dict): Execution input parameters
- `quality_preference` (str): "fast", "balanced", "premium", or "cost_optimized"
- `max_budget_per_task` (float, optional): Maximum budget per individual task

**Quality Preferences:**

| Preference | Strategy | Cost Impact | Performance |
|------------|----------|-------------|-------------|
| `fast` | Minimize latency | Lowest | Good |
| `balanced` | Balance cost/quality | Medium | Very Good |
| `premium` | Maximize quality | Highest | Excellent |
| `cost_optimized` | Minimize cost | Minimal | Good |

**Usage Example:**
```python
from workforce_api.services.hybrid_crew_extensions import create_hybrid_crew_from_team

# Execute team with hybrid routing
result = await create_hybrid_crew_from_team(
    team=team,
    execution_inputs={
        "project_description": "Create a marketing campaign for sustainable fashion",
        "target_audience": "Eco-conscious millennials",
        "budget": 10000,
        "timeline": "2 weeks"
    },
    quality_preference="balanced",
    max_budget_per_task=5.0
)

print(f"Execution result: {result['success']}")
print(f"Total cost: ${result['total_cost']}")

# Analyze routing decisions
for task_result in result['task_results']:
    print(f"Task: {task_result['task_name']}")
    print(f"  Provider: {task_result['llm_provider']}")
    print(f"  Cost: ${task_result['cost']}")
    print(f"  Reasoning: {task_result['routing_reasoning']}")
```

### Intelligent Agent Creation

The hybrid system creates agents with intelligent LLM routing:

```python
class HybridNuiFloAgent(NuiFloAgent):
    """Enhanced agent with intelligent LLM routing."""
    
    def __init__(
        self,
        role_model: Role,
        llm_router: IntelligentLLMRouter,
        quality_preference: str = "balanced",
        max_budget: Optional[float] = None,
        **kwargs
    ):
        # Initialize with router
        self.llm_router = llm_router
        self.quality_preference = quality_preference
        self.max_budget = max_budget
        
        # Call parent constructor
        super().__init__(role_model, **kwargs)
    
    async def execute_with_routing(self, task_prompt: str) -> Dict[str, Any]:
        """Execute task with intelligent LLM routing."""
        
        # Get routing decision
        routing_decision = self.llm_router.route_request(
            prompt=task_prompt,
            quality_preference=self.quality_preference,
            budget_limit=self.max_budget
        )
        
        # Execute with selected provider
        result = await self.llm_router.execute_request(
            routing_decision,
            task_prompt
        )
        
        return {
            "content": result.content,
            "provider": result.provider.value,
            "tokens_used": result.actual_tokens,
            "cost": result.actual_cost,
            "duration": result.duration_seconds,
            "routing_reasoning": routing_decision.reasoning
        }
```

### Budget Management

The hybrid system enforces budget constraints at multiple levels:

#### Team-Level Budget
```python
# Check team budget before execution
remaining_budget = team.monthly_budget - team.current_spend
if remaining_budget <= 0:
    raise HTTPException(400, "Team monthly budget exceeded")
```

#### Task-Level Budget
```python
# Enforce task budget limits
if max_budget_per_task:
    routing_decision = router.route_request(
        prompt=task_prompt,
        budget_limit=max_budget_per_task,
        quality_preference=quality_preference
    )
```

#### Real-Time Cost Tracking
```python
# Track costs during execution
total_cost = Decimal("0.00")
for task_result in task_results:
    total_cost += task_result["cost"]
    
    # Check if approaching budget limit
    if total_cost > (team.monthly_budget * 0.9):
        logger.warning("Approaching monthly budget limit", 
                      team_id=team.id, 
                      current_spend=float(total_cost))
```

---

## 🔧 Service Integration Patterns

### Repository Pattern

Services follow the repository pattern for data access:

```python
class TeamService:
    """Service layer handling business logic"""
    
    @staticmethod
    def create_team(...) -> Team:
        # Business logic
        # Validation
        # Database operations
        pass

# Usage in API endpoints
@router.post("/teams/")
async def create_team_endpoint(
    team_data: TeamCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    # Delegate to service layer
    team = TeamService.create_team(
        name=team_data.name,
        owner_id=current_user.id,
        monthly_budget=team_data.monthly_budget,
        session=db
    )
    return team
```

### Dependency Injection

Services support dependency injection for testing and flexibility:

```python
# Production usage with database
team = TeamService.create_team(
    name="Production Team",
    owner_id="user-id",
    monthly_budget=Decimal("500.00")
)

# Testing with mock session
with patch('workforce_api.core.database.SessionLocal') as mock_session:
    team = TeamService.create_team(
        name="Test Team",
        owner_id="test-user",
        monthly_budget=Decimal("100.00"),
        session=mock_session
    )
```

### Error Handling Patterns

Services implement consistent error handling:

```python
from structlog import get_logger
from fastapi import HTTPException

logger = get_logger()

@staticmethod
def create_team(...) -> Team:
    try:
        # Validation
        if not name or len(name.strip()) == 0:
            raise ValueError("Team name cannot be empty")
        
        if monthly_budget <= 0:
            raise ValueError("Monthly budget must be positive")
        
        # Business logic
        team = Team(...)
        db.add(team)
        db.commit()
        
        logger.info("Team created successfully", 
                   team_id=team.id, 
                   owner_id=owner_id)
        
        return team
        
    except ValueError as e:
        logger.error("Validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error creating team", 
                    error=str(e), 
                    exc_info=True)
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Service Composition

Services can be composed for complex operations:

```python
class TeamExecutionService:
    """High-level service composing multiple services"""
    
    def __init__(self):
        self.team_service = TeamService()
        self.llm_router = IntelligentLLMRouter()
    
    async def execute_team_with_tracking(
        self,
        team_id: int,
        execution_inputs: Dict[str, Any],
        quality_preference: str = "balanced"
    ) -> Dict[str, Any]:
        
        # 1. Get team information
        team = self.team_service.get_team_with_roles(team_id)
        if not team:
            raise HTTPException(404, "Team not found")
        
        # 2. Check budget constraints
        if team.current_spend >= team.monthly_budget:
            raise HTTPException(400, "Monthly budget exceeded")
        
        # 3. Execute with hybrid crew
        result = await create_hybrid_crew_from_team(
            team=team,
            execution_inputs=execution_inputs,
            quality_preference=quality_preference
        )
        
        # 4. Update team spending
        if result["success"]:
            self.team_service.update_team_spend(
                team_id=team_id,
                cost=result["total_cost"]
            )
        
        return result
```

### Testing Patterns

Services are designed for easy testing:

```python
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = Mock()
    return session

def test_create_team_success(mock_db_session):
    """Test successful team creation"""
    
    # Arrange
    team_data = {
        "name": "Test Team",
        "owner_id": "test-user",
        "monthly_budget": Decimal("100.00")
    }
    
    # Act
    with patch('workforce_api.core.database.SessionLocal', return_value=mock_db_session):
        team = TeamService.create_team(**team_data)
    
    # Assert
    assert team.name == "Test Team"
    assert team.monthly_budget == Decimal("100.00")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_create_team_validation_error():
    """Test team creation with invalid data"""
    
    with pytest.raises(HTTPException) as exc_info:
        TeamService.create_team(
            name="",  # Invalid empty name
            owner_id="test-user",
            monthly_budget=Decimal("100.00")
        )
    
    assert exc_info.value.status_code == 400
    assert "name cannot be empty" in str(exc_info.value.detail)
```

---

## 📊 Performance Monitoring

### Metrics Collection

Services automatically collect performance metrics:

```python
# Execution timing
start_time = time.time()
result = await execute_operation()
duration = time.time() - start_time

# Resource tracking
metrics = {
    "operation": "team_execution",
    "duration_seconds": duration,
    "tokens_used": result.tokens_used,
    "cost": float(result.cost),
    "success": result.success
}

logger.info("Operation completed", **metrics)
```

### Health Monitoring

Services provide health check capabilities:

```python
@staticmethod
def health_check() -> Dict[str, str]:
    """Check service health and dependencies"""
    
    status = {"service": "healthy"}
    
    try:
        # Test database connectivity
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    try:
        # Test LLM router
        router = IntelligentLLMRouter()
        test_decision = router.route_request("test prompt")
        status["llm_router"] = "operational"
    except Exception as e:
        status["llm_router"] = f"error: {str(e)}"
    
    return status
```

---

## 🔄 Usage Examples

### Complete Team Execution Workflow

```python
from workforce_api.services import TeamService
from workforce_api.services.hybrid_crew_extensions import create_hybrid_crew_from_team
from workforce_api.core.database import get_db_dependency
from fastapi import Depends

async def complete_team_execution_example(
    db: Session = Depends(get_db_dependency)
):
    """Complete example of team execution workflow"""
    
    # 1. Create team
    team = TeamService.create_team(
        name="Product Development Team",
        owner_id="550e8400-e29b-41d4-a716-446655440000",
        monthly_budget=Decimal("1000.00"),
        description="AI team for product development",
        roles_data=[
            {
                "title": "Product Manager",
                "expertise": "SENIOR",
                "llm_model": "gpt-4",
                "backstory": "Expert product manager with strategic thinking",
                "goals": ["Define product strategy", "Analyze market"]
            },
            {
                "title": "Developer",
                "expertise": "INTERMEDIATE", 
                "llm_model": "gpt-3.5-turbo",
                "backstory": "Experienced developer with full-stack skills",
                "goals": ["Design architecture", "Implement features"]
            }
        ],
        session=db
    )
    
    print(f"Created team: {team.name} (ID: {team.id})")
    
    # 2. Execute team task
    execution_result = await create_hybrid_crew_from_team(
        team=team,
        execution_inputs={
            "project_description": "Build a task management mobile app",
            "target_audience": "Remote teams and freelancers",
            "timeline": "3 months",
            "budget": 75000,
            "features": ["Task creation", "Team collaboration", "Time tracking"]
        },
        quality_preference="balanced",
        max_budget_per_task=10.0
    )
    
    # 3. Process results
    if execution_result["success"]:
        print("✅ Team execution completed successfully!")
        print(f"💰 Total cost: ${execution_result['total_cost']}")
        print(f"⏱️  Duration: {execution_result['execution_time_seconds']:.1f} seconds")
        
        # Update team spending
        updated_team = TeamService.update_team_spend(
            team_id=team.id,
            cost=execution_result["total_cost"],
            session=db
        )
        
        # Check budget status
        utilization = (updated_team.current_spend / updated_team.monthly_budget) * 100
        print(f"📊 Budget utilization: {utilization:.1f}%")
        
        # Display individual task results
        print("\n📋 Task Results:")
        for task_result in execution_result["task_results"]:
            print(f"  {task_result['agent_role']}: ${task_result['cost']:.2f} ({task_result['llm_provider']})")
    
    else:
        print("❌ Team execution failed!")
        print(f"Error: {execution_result['error']}")
    
    # 4. Get comprehensive team status
    status = TeamService.get_team_status(team.id, session=db)
    if status:
        print(f"\n📈 Team Performance:")
        print(f"  Total executions: {status['performance_metrics']['total_executions']}")
        print(f"  Success rate: {status['performance_metrics']['successful_executions']} / {status['performance_metrics']['total_executions']}")
        print(f"  Average cost: ${status['performance_metrics']['average_cost_per_execution']:.2f}")
    
    return {
        "team": team,
        "execution_result": execution_result,
        "status": status
    }
```

### Error Handling and Recovery

```python
async def robust_team_execution(team_id: int, execution_inputs: Dict[str, Any]):
    """Example with comprehensive error handling and recovery"""
    
    try:
        # Get team with validation
        team = TeamService.get_team_with_roles(team_id)
        if not team:
            raise HTTPException(404, "Team not found")
        
        # Validate budget
        if team.current_spend >= team.monthly_budget:
            raise HTTPException(400, "Monthly budget exceeded")
        
        # Validate team has active roles
        active_roles = [r for r in team.roles if r.is_active]
        if not active_roles:
            raise HTTPException(400, "Team has no active roles")
        
        # Execute with fallback strategies
        execution_result = await create_hybrid_crew_from_team(
            team=team,
            execution_inputs=execution_inputs,
            quality_preference="balanced"
        )
        
        if not execution_result["success"]:
            # Try with cost-optimized preference as fallback
            logger.warning("Execution failed, trying cost-optimized fallback", 
                          team_id=team_id)
            
            execution_result = await create_hybrid_crew_from_team(
                team=team,
                execution_inputs=execution_inputs,
                quality_preference="cost_optimized"
            )
        
        return execution_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error("Unexpected error in team execution", 
                    team_id=team_id, 
                    error=str(e), 
                    exc_info=True)
        raise HTTPException(500, "Internal server error")
```

---

**Next Steps**: [CrewAI Integration Documentation](CREWAI_INTEGRATION_DOCUMENTATION.md) | [Data Models Documentation](DATA_MODELS_DOCUMENTATION.md)