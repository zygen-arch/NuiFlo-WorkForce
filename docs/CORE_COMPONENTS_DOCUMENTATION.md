# NuiFlo WorkForce - Core Components Documentation

## 🧠 Overview

This document provides comprehensive documentation for all core components of the NuiFlo WorkForce platform, including configuration management, authentication, database operations, and the intelligent LLM routing system.

## 📋 Table of Contents

1. [Configuration System](#-configuration-system)
2. [Authentication & Security](#-authentication--security) 
3. [Database Layer](#-database-layer)
4. [Intelligent LLM Router](#-intelligent-llm-router)
5. [Rate Limiting & Security](#-rate-limiting--security)

---

## ⚙️ Configuration System

### Settings Class (`workforce_api.core.config`)

The configuration system uses Pydantic Settings for environment-based configuration with validation and type safety.

#### Key Features
- **Environment-based configuration** with `.env` file support
- **Automatic validation** and type conversion
- **Computed fields** for derived values
- **Production/development modes**

#### Configuration Structure

```python
from workforce_api.core.config import get_settings

settings = get_settings()  # Singleton pattern with caching
```

#### Environment Variables

| Category | Variable | Default | Description |
|----------|----------|---------|-------------|
| **Environment** | `ENVIRONMENT` | `development` | Environment mode (development/production) |
| **Database** | `DATABASE_URL` | - | Full PostgreSQL connection URL |
| | `DB_USER` | - | Database username |
| | `DB_PASSWORD` | - | Database password |
| | `DB_HOST` | - | Database host |
| | `DB_PORT` | `5432` | Database port |
| | `DB_NAME` | - | Database name |
| **Supabase** | `SUPABASE_URL` | - | Supabase project URL |
| | `SUPABASE_ANON_KEY` | - | Supabase anonymous key |
| | `SUPABASE_SERVICE_KEY` | - | Supabase service role key |
| **LLM Providers** | `OPENAI_API_KEY` | - | OpenAI API key |
| | `ANTHROPIC_API_KEY` | - | Anthropic API key |
| **Ollama** | `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| | `OLLAMA_MODEL` | `mistral:7b-instruct` | Default Ollama model |
| **App** | `DEBUG` | `False` | Enable debug mode |
| | `CORS_ORIGINS` | Multiple defaults | Allowed CORS origins |
| | `PORT` | `8000` | Server port |
| | `HOST` | `0.0.0.0` | Server host |

#### Usage Examples

```python
from workforce_api.core.config import get_settings

settings = get_settings()

# Check environment
if settings.is_production:
    # Production logic
    pass
elif settings.is_development:
    # Development logic
    pass

# Access database URL
db_url = settings.supabase_db_url

# Check auth configuration
if settings.auth_enabled:
    # Authentication is configured
    pass

# Access LLM settings
openai_key = settings.openai_api_key
ollama_host = settings.ollama_host
```

#### Computed Properties

```python
# Database URL construction
@computed_field
@property
def supabase_db_url(self) -> str:
    """Automatically constructs database URL from components or uses DATABASE_URL"""
    
# Environment checks
@property
def is_production(self) -> bool:
    return self.environment.lower() == "production"

@computed_field 
@property
def is_development(self) -> bool:
    return self.environment.lower() == "development"

# Authentication status
@computed_field
@property  
def auth_enabled(self) -> bool:
    return bool(self.supabase_url and self.supabase_anon_key)
```

---

## 🔐 Authentication & Security

### Supabase Authentication (`workforce_api.core.auth`)

The authentication system integrates with Supabase Auth for JWT-based authentication and authorization.

#### Key Features
- **JWT token validation** with Supabase
- **User context management**
- **Security middleware** integration
- **Role-based access control** (planned)

#### Authentication Flow

```python
from workforce_api.core.auth import get_current_user, verify_supabase_token
from fastapi import Depends

# Dependency for protected endpoints
@app.get("/protected")
async def protected_endpoint(user = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}
```

#### Authentication Functions

##### `verify_supabase_token(token: str)`
Verifies JWT token with Supabase and returns user information.

```python
# Manual token verification
user = await verify_supabase_token(token)
if user:
    print(f"User: {user.email}")
```

##### `get_current_user()`
FastAPI dependency for automatic user extraction from Authorization header.

```python
from fastapi import Depends
from workforce_api.core.auth import get_current_user

@router.get("/profile")
async def get_profile(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
```

#### User Model

```python
class SupabaseUser:
    id: str              # UUID from Supabase
    email: str           # User email
    role: str            # User role (authenticated/admin)
    aud: str             # Audience claim
    exp: int             # Token expiration
    iat: int             # Token issued at
    iss: str             # Token issuer
    sub: str             # Subject (user ID)
```

#### Error Handling

```python
from fastapi import HTTPException, status

# Authentication errors
HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Token format errors
HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token format"
)
```

#### Client Integration Example

```javascript
// Frontend: Get token from Supabase
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token

// Use in API calls
const response = await fetch('/api/v1/teams/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

---

## 🗄️ Database Layer

### Database Configuration (`workforce_api.core.database`)

The database layer provides SQLAlchemy integration with connection pooling, session management, and health monitoring.

#### Key Features
- **PostgreSQL/Supabase** integration
- **Connection pooling** for performance
- **Session management** with dependency injection
- **Database health monitoring**
- **Migration support** with Alembic

#### Database Setup

```python
from workforce_api.core.database import engine, SessionLocal, init_database

# Initialize database (called on app startup)
db_connected = init_database()

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Session Management

```python
from fastapi import Depends
from workforce_api.core.database import get_db_dependency

@router.post("/teams/")
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db_dependency)
):
    # Use database session
    team = Team(**team_data.dict())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team
```

#### Database Models Hierarchy

```
Base (SQLAlchemy declarative base)
├── Team
│   ├── id: int (PK)
│   ├── auth_owner_id: UUID (Supabase user)
│   ├── name: str
│   ├── monthly_budget: Decimal
│   └── roles: List[Role] (relationship)
├── Role  
│   ├── id: int (PK)
│   ├── team_id: int (FK)
│   ├── title: str
│   ├── expertise: ExpertiseLevel (enum)
│   └── llm_model: str
├── TeamExecution
│   ├── id: int (PK)
│   ├── team_id: int (FK)
│   ├── status: str
│   └── task_executions: List[TaskExecution]
└── TaskExecution
    ├── id: int (PK)
    ├── team_execution_id: int (FK)
    ├── role_id: int (FK)
    └── metrics: tokens, cost, duration
```

#### Health Monitoring

```python
# Check database connectivity
@router.get("/health/status")
async def health_status():
    status = {"database": "disconnected"}
    
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            status["database"] = "connected"
        except Exception as e:
            status["database"] = f"error: {str(e)}"
    
    return status
```

#### Connection Configuration

```python
# Database URL formats supported:
# 1. Full URL (Railway, Render, etc.)
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db

# 2. Component-based (individual settings)
DB_USER=username
DB_PASSWORD=password  
DB_HOST=localhost
DB_PORT=5432
DB_NAME=database
```

---

## 🧠 Intelligent LLM Router

### Overview (`workforce_api.core.intelligent_router`)

The Intelligent LLM Router is the brain of NuiFlo's hybrid AI system, automatically routing requests between local Ollama models and commercial LLM providers based on complexity analysis and cost optimization.

#### Key Features
- **Real-time complexity analysis** of prompts and tasks
- **Cost optimization** with budget-aware routing
- **Automatic fallback** when preferred models are unavailable
- **Performance tracking** and metrics collection
- **Multi-provider support** (Ollama, OpenAI, Anthropic)

#### Architecture Components

```python
# Core classes
IntelligentLLMRouter    # Main routing orchestrator  
ComplexityAnalyzer      # Task complexity analysis
LLMProvider            # Provider enumeration
RoutingDecision        # Routing decision with reasoning
ExecutionResult        # Execution tracking and metrics
```

### Complexity Analysis System

#### Complexity Levels

```python
class ComplexityLevel(Enum):
    SIMPLE = "simple"        # Ollama can handle
    MEDIUM = "medium"        # GPT-3.5 recommended
    COMPLEX = "complex"      # GPT-4 required  
    SPECIALIZED = "specialized"  # Domain-specific models
```

#### Analysis Heuristics

The complexity analyzer uses multiple heuristics to determine task complexity:

1. **Prompt Length Analysis**
   - Short prompts (< 100 chars) → SIMPLE
   - Medium prompts (100-500 chars) → MEDIUM
   - Long prompts (> 500 chars) → COMPLEX

2. **Keyword Detection**
   ```python
   # Complex reasoning keywords
   complex_keywords = [
       "analyze", "compare", "evaluate", "synthesize",
       "comprehensive", "detailed analysis", "strategic"
   ]
   
   # Specialized domain keywords  
   specialized_keywords = [
       "medical", "legal", "financial", "scientific",
       "technical documentation", "code review"
   ]
   ```

3. **Context Analysis**
   - Multiple entities or relationships → COMPLEX
   - Technical jargon density → SPECIALIZED
   - Abstract concepts → COMPLEX

#### Usage Example

```python
from workforce_api.core.intelligent_router import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()

# Analyze task complexity
prompt = "Write a comprehensive strategic analysis of the competitive landscape"
complexity = analyzer.analyze_complexity(prompt)
# Returns: ComplexityLevel.COMPLEX
```

### Routing Decision Engine

#### Routing Logic

```python
class IntelligentLLMRouter:
    def route_request(
        self, 
        prompt: str,
        context: Optional[str] = None,
        budget_limit: Optional[float] = None,
        quality_preference: str = "balanced"
    ) -> RoutingDecision:
```

#### Quality Preferences

| Preference | Strategy | Model Selection |
|------------|----------|-----------------|
| `fast` | Minimize latency | Ollama first, then GPT-3.5 |
| `balanced` | Balance cost/quality | GPT-3.5 for medium, GPT-4 for complex |
| `premium` | Maximize quality | GPT-4 first, Claude as backup |
| `cost_optimized` | Minimize cost | Ollama maximum, commercial minimal |

#### Routing Examples

```python
router = IntelligentLLMRouter()

# Simple task - routes to Ollama
decision = router.route_request(
    prompt="Write a hello world program in Python",
    quality_preference="balanced"
)
# Result: LLMProvider.OLLAMA_MISTRAL, cost=0.00

# Complex analysis - routes to GPT-4
decision = router.route_request(
    prompt="Analyze market trends and create strategic recommendations",
    quality_preference="premium"
)
# Result: LLMProvider.OPENAI_GPT_4, estimated_cost=0.15

# Budget-constrained - uses Ollama even for complex tasks
decision = router.route_request(
    prompt="Complex analysis task",
    budget_limit=0.01,
    quality_preference="cost_optimized"
)
# Result: LLMProvider.OLLAMA_MISTRAL, cost=0.00
```

### Provider Integration

#### Ollama Integration

```python
# HTTP-based Ollama integration (no Python client dependency)
async def execute_ollama_request(
    self,
    prompt: str,
    model: str = "mistral:7b-instruct"
) -> ExecutionResult:
    
    # Direct HTTP API call
    response = await httpx.post(
        f"{settings.ollama_host}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=30.0
    )
```

#### OpenAI Integration

```python
# OpenAI client integration
openai_client = OpenAI(api_key=settings.openai_api_key)

async def execute_openai_request(
    self,
    prompt: str,
    model: str = "gpt-3.5-turbo"
) -> ExecutionResult:
    
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
```

#### Anthropic Integration

```python
# Anthropic client integration  
anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

async def execute_anthropic_request(
    self,
    prompt: str,
    model: str = "claude-3-sonnet-20240229"
) -> ExecutionResult:
    
    response = await anthropic_client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
```

### Cost Calculation & Tracking

#### Token-based Pricing

```python
# Provider pricing (per 1K tokens)
PRICING = {
    LLMProvider.OLLAMA_MISTRAL: 0.0,      # Free local
    LLMProvider.OPENAI_GPT_35: 0.0015,    # $0.0015/1K tokens
    LLMProvider.OPENAI_GPT_4: 0.03,       # $0.03/1K tokens
    LLMProvider.ANTHROPIC_CLAUDE: 0.003,  # $0.003/1K tokens
}

def calculate_cost(
    self,
    tokens_used: int,
    provider: LLMProvider
) -> Decimal:
    rate = PRICING.get(provider, 0.0)
    return Decimal(str(tokens_used * rate / 1000))
```

#### Budget Management

```python
# Budget-aware routing
def check_budget_constraints(
    self,
    estimated_cost: Decimal,
    budget_limit: Optional[float]
) -> bool:
    if budget_limit is None:
        return True
    return estimated_cost <= Decimal(str(budget_limit))
```

### Performance Monitoring

#### Execution Tracking

```python
@dataclass
class ExecutionResult:
    content: str                    # Generated content
    provider: LLMProvider          # Provider used
    actual_tokens: int             # Tokens consumed
    actual_cost: Decimal           # Actual cost
    duration_seconds: float        # Execution time
    success: bool                  # Success status
    error: Optional[str] = None    # Error message if failed
```

#### Metrics Collection

```python
# Track routing decisions and outcomes
routing_metrics = {
    "total_requests": 0,
    "provider_usage": defaultdict(int),
    "avg_cost_per_request": 0.0,
    "avg_duration_seconds": 0.0,
    "success_rate": 0.0
}

# Log routing decisions
logger.info(
    "LLM routing decision",
    provider=decision.provider.value,
    complexity=decision.complexity.value,
    estimated_cost=float(decision.estimated_cost),
    reasoning=decision.reasoning
)
```

### Fallback Strategy

#### Automatic Fallback Chain

```python
# Primary -> Secondary -> Tertiary fallback
FALLBACK_CHAINS = {
    ComplexityLevel.SIMPLE: [
        LLMProvider.OLLAMA_MISTRAL,
        LLMProvider.OPENAI_GPT_35,
        LLMProvider.ANTHROPIC_CLAUDE
    ],
    ComplexityLevel.COMPLEX: [
        LLMProvider.OPENAI_GPT_4,
        LLMProvider.ANTHROPIC_CLAUDE,
        LLMProvider.OPENAI_GPT_35
    ]
}

async def execute_with_fallback(
    self,
    prompt: str,
    routing_decision: RoutingDecision
) -> ExecutionResult:
    
    fallback_chain = FALLBACK_CHAINS.get(routing_decision.complexity, [])
    
    for provider in fallback_chain:
        try:
            result = await self._execute_provider(provider, prompt)
            if result.success:
                return result
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            continue
    
    # All providers failed
    raise Exception("All LLM providers failed")
```

---

## 🛡️ Rate Limiting & Security

### Rate Limiting Middleware

#### Implementation

```python
class RateLimitMiddleware:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.window_seconds = 60
        
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        user_calls = rate_limit_storage[client_ip]
        while user_calls and user_calls[0] < current_time - self.window_seconds:
            user_calls.popleft()
        
        # Check rate limit
        if len(user_calls) >= self.calls_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
```

#### Configuration

```python
# Development: High limits for testing
rate_limiter = RateLimitMiddleware(calls_per_minute=10000)

# Production: Stricter limits
rate_limiter = RateLimitMiddleware(calls_per_minute=100)
```

### Security Headers

#### Headers Applied

```python
# Security headers added to all responses
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

# Content Security Policy (CSP)
response.headers["Content-Security-Policy"] = (
    "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "img-src 'self' data: https: blob:; "
    "connect-src 'self' https:;"
)
```

### Input Sanitization

#### String Sanitization

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
```

#### Model Validation

```python
# Pydantic model validation with sanitization
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_string(v)
    
    @field_validator('llm_model')
    @classmethod
    def validate_llm_model(cls, v):
        # Whitelist allowed models
        allowed_models = [
            'gpt-4', 'gpt-3.5-turbo', 'claude-3-sonnet',
            'mistral:7b-instruct', 'deepseek-coder:6.7b'
        ]
        if v not in allowed_models:
            raise ValueError(f'LLM model must be one of: {", ".join(allowed_models)}')
        return v
```

---

## 🔧 Usage Examples

### Complete Integration Example

```python
from workforce_api.core.config import get_settings
from workforce_api.core.auth import get_current_user
from workforce_api.core.database import get_db_dependency
from workforce_api.core.intelligent_router import IntelligentLLMRouter

@router.post("/teams/{team_id}/execute")
async def execute_team(
    team_id: int,
    execution_data: ExecutionRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    # 1. Get configuration
    settings = get_settings()
    
    # 2. Validate team ownership
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.auth_owner_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(404, "Team not found")
    
    # 3. Route LLM requests intelligently
    router = IntelligentLLMRouter()
    
    results = []
    for role in team.roles:
        # Route each role's task
        decision = router.route_request(
            prompt=execution_data.prompt,
            quality_preference=execution_data.quality_preference,
            budget_limit=float(team.monthly_budget - team.current_spend)
        )
        
        # Execute with selected provider
        result = await router.execute_request(decision, execution_data.prompt)
        results.append(result)
        
        # Update team spending
        team.current_spend += result.actual_cost
    
    # 4. Save execution record
    db.commit()
    
    return {
        "success": True,
        "results": results,
        "total_cost": sum(r.actual_cost for r in results)
    }
```

### Error Handling Pattern

```python
from structlog import get_logger

logger = get_logger()

try:
    # Core operation
    result = await some_operation()
    logger.info("Operation completed", result=result)
    
except ValidationError as e:
    logger.error("Validation failed", error=str(e))
    raise HTTPException(422, detail=str(e))
    
except Exception as e:
    logger.error("Unexpected error", error=str(e), exc_info=True)
    raise HTTPException(500, detail="Internal server error")
```

---

## 📈 Performance Considerations

### Database Optimization
- **Connection pooling** for concurrent requests
- **Eager loading** with `selectinload()` for relationships
- **Query optimization** with proper indexes
- **Session management** with proper cleanup

### LLM Router Optimization  
- **Caching** of complexity analysis results
- **Parallel execution** for multiple role tasks
- **Fallback strategies** for provider failures
- **Request batching** where possible

### Security Performance
- **In-memory rate limiting** (Redis recommended for production)
- **JWT validation caching** for repeated requests
- **Efficient string sanitization**
- **Optimized CSP policies**

---

## 🐛 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check connection
curl http://localhost:8000/health/status

# Verify environment variables
echo $DATABASE_URL
```

#### Ollama Connectivity
```bash
# Test Ollama directly
curl http://localhost:11434/api/version

# Check NuiFlo integration
curl http://localhost:8000/health/ollama-test
```

#### Authentication Issues
```bash
# Verify Supabase configuration
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test token validation
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/teams/
```

### Logging Configuration

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

---

**Next Steps**: [Services Documentation](SERVICES_DOCUMENTATION.md) | [CrewAI Integration Guide](CREWAI_INTEGRATION_DOCUMENTATION.md)