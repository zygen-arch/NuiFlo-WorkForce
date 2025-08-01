# NuiFlo WorkForce - Data Models Documentation

## 📊 Overview

This document provides comprehensive documentation for all data models in the NuiFlo WorkForce platform, including SQLAlchemy models, Pydantic schemas, validation rules, and database relationships.

## 📋 Table of Contents

1. [Database Models (SQLAlchemy)](#-database-models-sqlalchemy)
2. [API Schemas (Pydantic)](#-api-schemas-pydantic)
3. [Model Relationships](#-model-relationships)
4. [Validation Rules](#-validation-rules)
5. [Usage Examples](#-usage-examples)

---

## 🗄️ Database Models (SQLAlchemy)

### Base Configuration

All models inherit from a common base with standardized configuration:

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
```

### Team Model

#### Overview
The Team model represents a collection of AI agents working together on tasks with shared budget and configuration.

```python
class Team(Base):
    __tablename__ = "teams"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Owner Information
    auth_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Supabase user UUID
    owner_id = Column(Integer, nullable=True)  # Legacy field for backward compatibility
    
    # Basic Information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Budget Management
    monthly_budget = Column(Numeric(10, 2), nullable=False)
    current_spend = Column(Numeric(10, 2), default=0.0)
    
    # Status Tracking
    status = Column(SQLEnum(TeamStatus), default=TeamStatus.IDLE)
    last_executed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", back_populates="team", cascade="all, delete-orphan")
    executions = relationship("TeamExecution", back_populates="team", cascade="all, delete-orphan")
```

#### Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | Integer | Primary key, auto-increment | NOT NULL, PRIMARY KEY |
| `auth_owner_id` | UUID | Supabase user UUID (new auth system) | Indexed |
| `owner_id` | Integer | Legacy owner ID (backward compatibility) | Nullable |
| `name` | String(100) | Team display name | NOT NULL, max 100 chars |
| `description` | Text | Optional team description | Nullable |
| `monthly_budget` | Numeric(10,2) | Monthly budget in USD | NOT NULL, precision 10, scale 2 |
| `current_spend` | Numeric(10,2) | Current month spending | Default 0.0 |
| `status` | Enum | Current team status | Default IDLE |
| `last_executed_at` | DateTime | Timestamp of last execution | Nullable |
| `created_at` | DateTime | Creation timestamp | Default now() |
| `updated_at` | DateTime | Last update timestamp | Auto-updated |

#### Team Status Enum

```python
class TeamStatus(Enum):
    IDLE = "IDLE"           # Team ready for execution
    RUNNING = "RUNNING"     # Team currently executing
    COMPLETED = "COMPLETED" # Team completed execution
    FAILED = "FAILED"       # Team execution failed
```

#### Usage Example

```python
from workforce_api.models import Team, TeamStatus
from decimal import Decimal

# Create new team
team = Team(
    auth_owner_id="550e8400-e29b-41d4-a716-446655440000",
    name="Marketing Team",
    description="AI team for marketing campaigns",
    monthly_budget=Decimal("500.00"),
    status=TeamStatus.IDLE
)

# Add to database
db.add(team)
db.commit()
db.refresh(team)

print(f"Created team: {team.name} (ID: {team.id})")
```

### Role Model

#### Overview
The Role model represents individual AI agents within a team with specific expertise and LLM configuration.

```python
class Role(Base):
    __tablename__ = "roles"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Role Information
    title = Column(String(100), nullable=False)
    description = Column(Text)
    expertise = Column(Enum(ExpertiseLevel), nullable=False)
    
    # LLM Configuration
    llm_model = Column(String(50), nullable=False, default="gpt-3.5-turbo")
    llm_config = Column(JSON)  # Model parameters (temperature, max_tokens, etc.)
    
    # Agent Configuration
    agent_config = Column(JSON)  # CrewAI agent config (tools, backstory, etc.)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="roles")
    task_executions = relationship("TaskExecution", back_populates="role")
```

#### Expertise Level Enum

```python
class ExpertiseLevel(enum.Enum):
    JUNIOR = "junior"           # Junior level expertise
    INTERMEDIATE = "intermediate" # Intermediate level expertise
    SENIOR = "senior"           # Senior level expertise
    EXPERT = "expert"           # Expert level expertise
```

#### Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | Integer | Primary key, auto-increment | NOT NULL, PRIMARY KEY |
| `team_id` | Integer | Foreign key to teams table | NOT NULL, FOREIGN KEY |
| `title` | String(100) | Role title/name | NOT NULL, max 100 chars |
| `description` | Text | Optional role description | Nullable |
| `expertise` | Enum | Expertise level | NOT NULL |
| `llm_model` | String(50) | LLM model identifier | NOT NULL, default "gpt-3.5-turbo" |
| `llm_config` | JSON | LLM parameters | Nullable |
| `agent_config` | JSON | CrewAI agent configuration | Nullable |
| `is_active` | Boolean | Whether role is active | Default True |
| `created_at` | DateTime | Creation timestamp | Default now() |
| `updated_at` | DateTime | Last update timestamp | Auto-updated |

#### Configuration Examples

##### LLM Config Structure
```python
llm_config = {
    "temperature": 0.7,      # Creativity level (0.0-1.0)
    "max_tokens": 2000,      # Maximum tokens to generate
    "top_p": 0.9,           # Nucleus sampling parameter
    "frequency_penalty": 0.0, # Frequency penalty
    "presence_penalty": 0.0   # Presence penalty
}
```

##### Agent Config Structure
```python
agent_config = {
    "backstory": "Expert marketing strategist with 10+ years experience",
    "goals": [
        "Create compelling marketing content",
        "Analyze market trends and opportunities",
        "Develop strategic recommendations"
    ],
    "tools": [
        "market_research",
        "content_analysis", 
        "competitor_analysis"
    ],
    "system_prompt": "You are a senior marketing strategist...",
    "allow_delegation": False,
    "verbose": True
}
```

#### Usage Example

```python
from workforce_api.models import Role, ExpertiseLevel

# Create role with configuration
role = Role(
    team_id=1,
    title="Content Strategist",
    description="Develops content strategies and marketing plans",
    expertise=ExpertiseLevel.SENIOR,
    llm_model="gpt-4",
    llm_config={
        "temperature": 0.7,
        "max_tokens": 2000
    },
    agent_config={
        "backstory": "Expert content strategist with deep marketing knowledge",
        "goals": ["Create engaging content", "Analyze audience needs"],
        "tools": ["content_analysis", "market_research"]
    },
    is_active=True
)

db.add(role)
db.commit()
```

### Execution Models

#### TeamExecution Model

Tracks team-level execution with aggregated metrics and results.

```python
class TeamExecution(Base):
    __tablename__ = "team_executions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Execution Status
    status = Column(String, nullable=False, default=TeamStatus.RUNNING.value)
    
    # Results
    result = Column(Text)           # Final crew output
    error_message = Column(Text)    # Error message if failed
    execution_metadata = Column(JSON)  # Input params, context
    
    # Resource Tracking
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 4), default=0)  # Higher precision for cost
    duration_seconds = Column(Numeric(10, 2))
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="executions")
    task_executions = relationship("TaskExecution", back_populates="team_execution", cascade="all, delete-orphan")
```

#### TaskExecution Model

Tracks individual task execution within a team execution.

```python
class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    team_execution_id = Column(Integer, ForeignKey("team_executions.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Task Information
    task_name = Column(String(100), nullable=False)
    task_description = Column(Text)
    status = Column(String, nullable=False, default=TeamStatus.RUNNING.value)
    
    # Task Data
    input_data = Column(JSON)   # Task input parameters
    output_data = Column(JSON)  # Task output/results
    error_message = Column(Text) # Error message if failed
    
    # Resource Tracking
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 4), default=0)
    duration_seconds = Column(Numeric(10, 2))
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team_execution = relationship("TeamExecution", back_populates="task_executions")
    role = relationship("Role", back_populates="task_executions")
```

#### Usage Example

```python
from workforce_api.models import TeamExecution, TaskExecution, TeamStatus
from decimal import Decimal

# Create team execution
team_execution = TeamExecution(
    team_id=1,
    status=TeamStatus.RUNNING.value,
    execution_metadata={
        "project_description": "Build mobile app",
        "timeline": "3 months",
        "budget": 50000
    }
)

db.add(team_execution)
db.flush()  # Get ID without committing

# Create task execution
task_execution = TaskExecution(
    team_execution_id=team_execution.id,
    role_id=1,
    task_name="Market Analysis",
    task_description="Analyze target market and competition",
    input_data={"market": "mobile apps", "audience": "millennials"},
    tokens_used=1500,
    cost=Decimal("0.045"),
    duration_seconds=Decimal("89.5")
)

db.add(task_execution)
db.commit()
```

### User Model

#### Overview
Simple user model for basic user information (mainly used for legacy compatibility).

```python
class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Note**: In production, user authentication is handled by Supabase. This model is primarily for legacy compatibility and testing.

---

## 📄 API Schemas (Pydantic)

### Base Configuration

All Pydantic models use consistent configuration:

```python
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,    # Allow creation from SQLAlchemy models
        validate_assignment=True, # Validate on assignment
        str_strip_whitespace=True # Strip whitespace from strings
    )
```

### Team Schemas

#### TeamCreate Schema

Used for creating new teams via API.

```python
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=1000, description="Team description")
    monthly_budget: Decimal = Field(..., gt=0, le=10000, description="Monthly budget in USD (max $10,000)")
    roles: List[RoleCreate] = Field(default_factory=list, max_length=10, description="Team roles")
    
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
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Marketing Team",
                "description": "AI team for marketing campaigns",
                "monthly_budget": 500.00,
                "roles": [
                    {
                        "title": "Content Strategist",
                        "expertise": "senior",
                        "llm_model": "gpt-4"
                    }
                ]
            }
        }
    )
```

#### TeamUpdate Schema

Used for updating existing teams.

```python
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
```

#### TeamResponse Schema

Used for returning team data from API.

```python
class TeamResponse(BaseModel):
    id: int
    auth_owner_id: Optional[str] = None
    owner_id: Optional[int] = None  # Legacy field
    name: str
    description: Optional[str] = None
    monthly_budget: str  # Decimal serialized as string
    current_spend: str   # Decimal serialized as string
    status: str
    last_executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List['RoleResponse'] = []
    
    @field_serializer('monthly_budget', 'current_spend')
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value)
    
    @field_serializer('last_executed_at', 'created_at', 'updated_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None
    
    model_config = ConfigDict(from_attributes=True)
```

### Role Schemas

#### RoleCreate Schema

```python
class RoleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Role title")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    expertise: ExpertiseLevel = Field(..., description="Expertise level")
    llm_model: str = Field(default="gpt-3.5-turbo", max_length=50, description="LLM model")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM configuration")
    agent_config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    is_active: bool = Field(True, description="Whether role is active")
    
    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v):
        return sanitize_string(v)
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @field_validator('llm_model')
    @classmethod
    def validate_llm_model(cls, v):
        allowed_models = [
            # OpenAI Models
            'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo',
            # Anthropic Models  
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
            # Ollama Models
            'deepseek-coder:6.7b', 'deepseek-coder:33b', 'deepseek-coder:1.3b',
            'llama2:7b', 'llama2:13b', 'llama2:70b',
            'mistral:7b', 'mistral:13b',
            'codellama:7b', 'codellama:13b', 'codellama:34b',
            'neural-chat:7b', 'neural-chat:13b'
        ]
        if v not in allowed_models:
            raise ValueError(f'LLM model must be one of: {", ".join(allowed_models)}')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Content Strategist",
                "description": "Develops content strategies",
                "expertise": "senior",
                "llm_model": "gpt-4",
                "llm_config": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "agent_config": {
                    "backstory": "Expert strategist",
                    "goals": ["Create content", "Analyze trends"]
                },
                "is_active": True
            }
        }
    )
```

#### RoleResponse Schema

```python
class RoleResponse(BaseModel):
    id: int
    team_id: int
    title: str
    description: Optional[str] = None
    expertise: str  # Enum serialized as string
    llm_model: str
    llm_config: Optional[Dict[str, Any]] = None
    agent_config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('expertise')
    def serialize_expertise(self, value: ExpertiseLevel) -> str:
        return value.value
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()
    
    model_config = ConfigDict(from_attributes=True)
```

### Execution Schemas

#### TeamExecutionRequest Schema

```python
class TeamExecutionRequest(BaseModel):
    inputs: Dict[str, Any] = Field(..., description="Execution input parameters")
    execution_config: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "max_iterations": 5,
            "timeout_minutes": 30,
            "quality_preference": "balanced"
        },
        description="Execution configuration"
    )
    
    @field_validator('inputs')
    @classmethod
    def validate_inputs(cls, v):
        # Ensure inputs is not empty
        if not v:
            raise ValueError("Inputs cannot be empty")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inputs": {
                    "project_description": "Build a mobile app for food delivery",
                    "timeline": "3 months",
                    "budget": 50000,
                    "target_audience": "Urban millennials"
                },
                "execution_config": {
                    "max_iterations": 5,
                    "timeout_minutes": 30,
                    "quality_preference": "balanced"
                }
            }
        }
    )
```

#### TeamExecutionResponse Schema

```python
class TeamExecutionResponse(BaseModel):
    success: bool
    team_execution_id: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @field_serializer('started_at', 'completed_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "team_execution_id": 123,
                "result": "Comprehensive marketing strategy developed...",
                "metrics": {
                    "execution_time_seconds": 245.7,
                    "total_tokens_used": 8750,
                    "total_cost": 12.45,
                    "tasks_completed": 8,
                    "agents_involved": 2
                },
                "breakdown": [
                    {
                        "role": "Content Strategist",
                        "task": "Strategy Development",
                        "tokens_used": 2500,
                        "cost": 3.75,
                        "duration_seconds": 89.2
                    }
                ]
            }
        }
    )
```

### Status and Info Schemas

#### TeamStatusResponse Schema

```python
class TeamStatusResponse(BaseModel):
    team_id: int
    name: str
    status: str
    monthly_budget: float
    current_spend: float
    budget_utilization: float  # Percentage (0-100)
    last_executed_at: Optional[datetime] = None
    role_count: int
    active_roles: int
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    @field_serializer('last_executed_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": 123,
                "name": "Marketing Team",
                "status": "idle",
                "monthly_budget": 500.0,
                "current_spend": 45.75,
                "budget_utilization": 9.15,
                "last_executed_at": "2025-01-27T10:30:00",
                "role_count": 2,
                "active_roles": 2,
                "performance_metrics": {
                    "total_executions": 5,
                    "successful_executions": 4,
                    "average_duration_seconds": 120.5,
                    "total_tokens_used": 12500
                }
            }
        }
    )
```

---

## 🔗 Model Relationships

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │      Team       │
│                 │       │                 │
│ id (PK)         │       │ id (PK)         │
│ email           │       │ auth_owner_id   │
│ username        │       │ name            │
│ is_active       │       │ monthly_budget  │
│ created_at      │       │ current_spend   │
│ updated_at      │       │ status          │
└─────────────────┘       │ created_at      │
                          │ updated_at      │
                          └─────────┬───────┘
                                    │
                                    │ 1:N
                                    │
                          ┌─────────▼───────┐
                          │      Role       │
                          │                 │
                          │ id (PK)         │
                          │ team_id (FK)    │
                          │ title           │
                          │ expertise       │
                          │ llm_model       │
                          │ llm_config      │
                          │ agent_config    │
                          │ is_active       │
                          └─────────┬───────┘
                                    │
                                    │ 1:N
                                    │
┌─────────────────┐       ┌─────────▼───────┐       ┌─────────────────┐
│ TeamExecution   │◄──────┤ TaskExecution   │──────►│      Role       │
│                 │  1:N  │                 │  N:1  │   (reference)   │
│ id (PK)         │       │ id (PK)         │       └─────────────────┘
│ team_id (FK)    │       │ team_execution_id (FK) │
│ status          │       │ role_id (FK)    │
│ result          │       │ task_name       │
│ tokens_used     │       │ input_data      │
│ cost            │       │ output_data     │
│ duration        │       │ tokens_used     │
│ started_at      │       │ cost            │
│ completed_at    │       │ duration        │
└─────────────────┘       └─────────────────┘
        ▲
        │ 1:N
        │
┌───────┴───────┐
│     Team      │
│ (reference)   │
└───────────────┘
```

### Relationship Details

#### Team → Roles (One-to-Many)
```python
# Team model
roles = relationship("Role", back_populates="team", cascade="all, delete-orphan")

# Role model  
team = relationship("Team", back_populates="roles")
```

**Cascade Behavior**: When a team is deleted, all associated roles are automatically deleted.

#### Team → TeamExecutions (One-to-Many)
```python
# Team model
executions = relationship("TeamExecution", back_populates="team", cascade="all, delete-orphan")

# TeamExecution model
team = relationship("Team", back_populates="executions")
```

#### TeamExecution → TaskExecutions (One-to-Many)
```python
# TeamExecution model
task_executions = relationship("TaskExecution", back_populates="team_execution", cascade="all, delete-orphan")

# TaskExecution model
team_execution = relationship("TeamExecution", back_populates="task_executions")
```

#### Role → TaskExecutions (One-to-Many)
```python
# Role model
task_executions = relationship("TaskExecution", back_populates="role")

# TaskExecution model
role = relationship("Role", back_populates="task_executions")
```

### Query Examples

#### Loading Related Data

```python
# Load team with roles (eager loading)
team = db.query(Team).options(
    selectinload(Team.roles)
).filter(Team.id == 1).first()

# Load team with executions and task details
team = db.query(Team).options(
    selectinload(Team.executions).selectinload(TeamExecution.task_executions)
).filter(Team.id == 1).first()

# Load role with team and task executions
role = db.query(Role).options(
    selectinload(Role.team),
    selectinload(Role.task_executions)
).filter(Role.id == 1).first()
```

#### Complex Queries

```python
# Get teams with budget utilization > 80%
high_utilization_teams = db.query(Team).filter(
    (Team.current_spend / Team.monthly_budget) > 0.8
).all()

# Get active roles for a specific LLM model
gpt4_roles = db.query(Role).filter(
    Role.llm_model == "gpt-4",
    Role.is_active == True
).all()

# Get successful executions with cost breakdown
successful_executions = db.query(TeamExecution).filter(
    TeamExecution.status == "COMPLETED"
).options(
    selectinload(TeamExecution.task_executions)
).all()
```

---

## ✅ Validation Rules

### Field Validation

#### String Validation
```python
def sanitize_string(value: str) -> str:
    """Sanitize string input to prevent XSS attacks."""
    if not isinstance(value, str):
        return value
    
    # Remove HTML tags and escape special characters
    value = re.sub(r'<[^>]*>', '', value)  # Remove HTML tags
    value = html.escape(value)             # Escape HTML characters
    value = value.strip()                  # Remove whitespace
    
    return value

# Applied in Pydantic models
@field_validator('name')
@classmethod
def sanitize_name(cls, v):
    return sanitize_string(v)
```

#### Decimal Validation
```python
# Budget validation
monthly_budget: Decimal = Field(
    ..., 
    gt=0,           # Must be greater than 0
    le=10000,       # Maximum $10,000
    decimal_places=2, # 2 decimal places
    description="Monthly budget in USD"
)
```

#### List Validation
```python
# Roles list validation
roles: List[RoleCreate] = Field(
    default_factory=list,
    max_length=10,  # Maximum 10 roles per team
    description="Team roles"
)
```

#### Enum Validation
```python
# Expertise level validation (automatic with enum)
expertise: ExpertiseLevel = Field(
    ...,
    description="Must be one of: junior, intermediate, senior, expert"
)
```

### Business Logic Validation

#### Team Creation Validation
```python
def validate_team_creation(team_data: TeamCreate) -> None:
    """Validate team creation business rules."""
    
    # Check role titles are unique
    role_titles = [role.title for role in team_data.roles]
    if len(role_titles) != len(set(role_titles)):
        raise ValueError("Role titles must be unique within a team")
    
    # Check at least one role if roles provided
    if team_data.roles and not any(role.is_active for role in team_data.roles):
        raise ValueError("Team must have at least one active role")
    
    # Validate LLM model availability
    for role in team_data.roles:
        if not is_llm_model_available(role.llm_model):
            raise ValueError(f"LLM model '{role.llm_model}' is not available")
```

#### Budget Validation
```python
def validate_execution_budget(team: Team, estimated_cost: Decimal) -> None:
    """Validate execution against team budget."""
    
    remaining_budget = team.monthly_budget - team.current_spend
    
    if remaining_budget <= 0:
        raise ValueError("Monthly budget exceeded")
    
    if estimated_cost > remaining_budget:
        raise ValueError(f"Estimated cost ${estimated_cost} exceeds remaining budget ${remaining_budget}")
    
    # Warning if approaching budget limit
    if (team.current_spend + estimated_cost) > (team.monthly_budget * 0.9):
        logger.warning("Approaching budget limit", 
                      team_id=team.id,
                      utilization=(team.current_spend + estimated_cost) / team.monthly_budget * 100)
```

### Database Constraints

#### Table Constraints
```sql
-- Teams table constraints
ALTER TABLE teams 
ADD CONSTRAINT ck_teams_monthly_budget_positive 
CHECK (monthly_budget > 0);

ALTER TABLE teams 
ADD CONSTRAINT ck_teams_current_spend_non_negative 
CHECK (current_spend >= 0);

-- Roles table constraints  
ALTER TABLE roles
ADD CONSTRAINT ck_roles_title_not_empty
CHECK (LENGTH(TRIM(title)) > 0);

-- Execution constraints
ALTER TABLE team_executions
ADD CONSTRAINT ck_team_executions_cost_non_negative
CHECK (cost >= 0);

ALTER TABLE task_executions  
ADD CONSTRAINT ck_task_executions_tokens_non_negative
CHECK (tokens_used >= 0);
```

#### Index Constraints
```sql
-- Unique constraints
CREATE UNIQUE INDEX idx_teams_name_owner 
ON teams(name, auth_owner_id) 
WHERE auth_owner_id IS NOT NULL;

-- Performance indexes
CREATE INDEX idx_teams_owner_status ON teams(auth_owner_id, status);
CREATE INDEX idx_roles_team_active ON roles(team_id, is_active);
CREATE INDEX idx_executions_team_status ON team_executions(team_id, status);
```

---

## 💡 Usage Examples

### Complete CRUD Operations

#### Team Management
```python
from workforce_api.models import Team, Role, ExpertiseLevel
from workforce_api.core.database import SessionLocal
from decimal import Decimal

def team_crud_example():
    """Complete example of team CRUD operations."""
    
    with SessionLocal() as db:
        # CREATE
        team = Team(
            auth_owner_id="550e8400-e29b-41d4-a716-446655440000",
            name="Development Team",
            description="AI team for software development",
            monthly_budget=Decimal("800.00")
        )
        db.add(team)
        db.flush()  # Get ID without committing
        
        # Add roles
        roles_data = [
            {
                "title": "Lead Developer",
                "expertise": ExpertiseLevel.SENIOR,
                "llm_model": "gpt-4",
                "description": "Senior full-stack developer"
            },
            {
                "title": "QA Engineer", 
                "expertise": ExpertiseLevel.INTERMEDIATE,
                "llm_model": "gpt-3.5-turbo",
                "description": "Quality assurance specialist"
            }
        ]
        
        for role_data in roles_data:
            role = Role(team_id=team.id, **role_data)
            db.add(role)
        
        db.commit()
        print(f"Created team: {team.name} (ID: {team.id})")
        
        # READ
        # Get team with roles
        team_with_roles = db.query(Team).options(
            selectinload(Team.roles)
        ).filter(Team.id == team.id).first()
        
        print(f"Team has {len(team_with_roles.roles)} roles:")
        for role in team_with_roles.roles:
            print(f"  - {role.title} ({role.expertise.value})")
        
        # UPDATE
        team.description = "Updated: AI team for agile software development"
        team.monthly_budget = Decimal("1000.00")
        db.commit()
        print(f"Updated team budget to ${team.monthly_budget}")
        
        # DELETE (cascades to roles)
        db.delete(team)
        db.commit()
        print("Team deleted (roles automatically deleted)")
```

#### Execution Tracking
```python
from workforce_api.models import TeamExecution, TaskExecution, TeamStatus
from datetime import datetime

def execution_tracking_example():
    """Example of execution tracking."""
    
    with SessionLocal() as db:
        # Start team execution
        team_execution = TeamExecution(
            team_id=1,
            status=TeamStatus.RUNNING.value,
            execution_metadata={
                "project": "E-commerce Website",
                "timeline": "6 weeks",
                "requirements": ["User auth", "Product catalog", "Payment"]
            },
            started_at=datetime.utcnow()
        )
        db.add(team_execution)
        db.flush()
        
        # Track individual tasks
        tasks = [
            {
                "role_id": 1,
                "task_name": "Architecture Design",
                "task_description": "Design system architecture",
                "input_data": {"requirements": ["scalability", "security"]},
                "tokens_used": 2500,
                "cost": Decimal("0.075"),
                "duration_seconds": Decimal("120.5")
            },
            {
                "role_id": 2,
                "task_name": "Test Planning",
                "task_description": "Create comprehensive test plan",
                "input_data": {"scope": "full application"},
                "tokens_used": 1800,
                "cost": Decimal("0.027"),
                "duration_seconds": Decimal("95.2")
            }
        ]
        
        total_cost = Decimal("0.00")
        total_tokens = 0
        
        for task_data in tasks:
            task_execution = TaskExecution(
                team_execution_id=team_execution.id,
                **task_data,
                status=TeamStatus.COMPLETED.value,
                completed_at=datetime.utcnow()
            )
            db.add(task_execution)
            
            total_cost += task_data["cost"]
            total_tokens += task_data["tokens_used"]
        
        # Complete team execution
        team_execution.status = TeamStatus.COMPLETED.value
        team_execution.result = "Successfully designed e-commerce architecture and test plan"
        team_execution.cost = total_cost
        team_execution.tokens_used = total_tokens
        team_execution.completed_at = datetime.utcnow()
        
        # Update team spending
        team = db.query(Team).filter(Team.id == 1).first()
        team.current_spend += total_cost
        team.last_executed_at = datetime.utcnow()
        
        db.commit()
        
        print(f"Execution completed:")
        print(f"  Total cost: ${total_cost}")
        print(f"  Total tokens: {total_tokens}")
        print(f"  Tasks completed: {len(tasks)}")
```

#### Complex Queries
```python
def analytics_example():
    """Example of analytics queries."""
    
    with SessionLocal() as db:
        # Team performance analytics
        from sqlalchemy import func, desc
        
        # Top teams by execution count
        top_teams = db.query(
            Team.name,
            func.count(TeamExecution.id).label('execution_count'),
            func.avg(TeamExecution.cost).label('avg_cost'),
            func.sum(TeamExecution.cost).label('total_cost')
        ).join(TeamExecution).group_by(Team.id, Team.name).order_by(
            desc('execution_count')
        ).limit(10).all()
        
        print("Top Teams by Execution Count:")
        for team in top_teams:
            print(f"  {team.name}: {team.execution_count} executions, "
                  f"avg cost: ${team.avg_cost:.2f}")
        
        # Role utilization analysis
        role_usage = db.query(
            Role.title,
            Role.llm_model,
            func.count(TaskExecution.id).label('task_count'),
            func.avg(TaskExecution.duration_seconds).label('avg_duration'),
            func.sum(TaskExecution.cost).label('total_cost')
        ).join(TaskExecution).group_by(
            Role.id, Role.title, Role.llm_model
        ).order_by(desc('task_count')).all()
        
        print("\nRole Utilization:")
        for role in role_usage:
            print(f"  {role.title} ({role.llm_model}): "
                  f"{role.task_count} tasks, "
                  f"avg duration: {role.avg_duration:.1f}s")
        
        # Budget utilization by team
        budget_analysis = db.query(
            Team.name,
            Team.monthly_budget,
            Team.current_spend,
            ((Team.current_spend / Team.monthly_budget) * 100).label('utilization_pct')
        ).filter(Team.current_spend > 0).order_by(desc('utilization_pct')).all()
        
        print("\nBudget Utilization:")
        for team in budget_analysis:
            print(f"  {team.name}: {team.utilization_pct:.1f}% "
                  f"(${team.current_spend}/${team.monthly_budget})")
```

#### Model Serialization
```python
def serialization_example():
    """Example of model serialization for API responses."""
    
    with SessionLocal() as db:
        # Get team with all relationships
        team = db.query(Team).options(
            selectinload(Team.roles),
            selectinload(Team.executions).selectinload(TeamExecution.task_executions)
        ).filter(Team.id == 1).first()
        
        if team:
            # Convert to Pydantic model for API response
            team_response = TeamResponse.model_validate(team)
            
            # Serialize to JSON
            team_json = team_response.model_dump_json(indent=2)
            print("Team JSON Response:")
            print(team_json)
            
            # Custom serialization with calculations
            team_dict = {
                "id": team.id,
                "name": team.name,
                "budget_utilization": float(team.current_spend / team.monthly_budget * 100),
                "role_count": len(team.roles),
                "active_roles": len([r for r in team.roles if r.is_active]),
                "execution_count": len(team.executions),
                "last_execution": team.last_executed_at.isoformat() if team.last_executed_at else None,
                "roles": [
                    {
                        "id": role.id,
                        "title": role.title,
                        "expertise": role.expertise.value,
                        "llm_model": role.llm_model,
                        "is_active": role.is_active
                    }
                    for role in team.roles
                ]
            }
            
            print("\nCustom Team Dictionary:")
            import json
            print(json.dumps(team_dict, indent=2))
```

---

**Next Steps**: [CrewAI Integration Documentation](CREWAI_INTEGRATION_DOCUMENTATION.md) | [Developer Guide](DEVELOPER_GUIDE.md)