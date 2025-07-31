# NuiFlo WorkForce API - Comprehensive Documentation

![NuiFlo WorkForce](https://img.shields.io/badge/NuiFlo-WorkForce-blue) ![Version](https://img.shields.io/badge/version-0.1.0-green) ![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Overview

NuiFlo WorkForce is an AI-powered virtual team management platform that allows you to create, deploy, and manage teams of AI agents using CrewAI. The platform supports multiple LLM providers including local Ollama models, OpenAI, and Anthropic.

### Key Features

- **Team Management**: Create and manage AI teams with custom roles
- **Intelligent LLM Routing**: Automatic optimization between local and cloud models
- **Role Configuration**: Define agent expertise levels and LLM models
- **Budget Tracking**: Monitor spending and set monthly budgets
- **Real-time Execution**: Execute teams using CrewAI framework
- **Status Monitoring**: Track team performance and utilization

### Base Information

- **Base URL**: `https://api.nuiflo.com` (Production) / `http://localhost:8000` (Development)
- **API Version**: `v1`
- **Authentication**: Bearer Token (Supabase JWT)
- **Content Type**: `application/json`

## 📚 Interactive Documentation

- **Swagger UI**: [/docs](http://localhost:8000/docs)
- **ReDoc**: [/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [/openapi.json](http://localhost:8000/openapi.json)

## 🔐 Authentication

All API endpoints (except health checks) require authentication using Supabase JWT tokens.

### Authentication Header
```http
Authorization: Bearer <your_jwt_token>
```

### Getting Started with Auth

1. **Register/Login** through Supabase client
2. **Get JWT Token** from Supabase session
3. **Include token** in all API requests

```javascript
// Example: Get token from Supabase
const { data: { user } } = await supabase.auth.getUser()
const token = user.access_token

// Use in API calls
const response = await fetch('/api/v1/teams/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

## 🏥 Health Endpoints

### Ping Check
```http
GET /health/ping
```

Basic connectivity test.

**Response:**
```json
{
  "message": "pong",
  "timestamp": "2025-01-27T13:16:25.292087"
}
```

### System Status
```http
GET /health/status
```

Comprehensive health check including database connectivity.

**Response:**
```json
{
  "api": "healthy",
  "timestamp": "2025-01-27T13:16:25.292087",
  "database": "connected"
}
```

### Ollama Connectivity Test
```http
GET /health/ollama-test
```

Test local Ollama model connectivity and response.

**Response:**
```json
{
  "ollama_status": "connected",
  "model": "mistral:7b-instruct",
  "test_response": "Hello! I'm working correctly.",
  "response_time_ms": 1250
}
```

### CrewAI Integration Test
```http
GET /health/crewai-test
```

Test CrewAI framework integration and agent creation.

**Response:**
```json
{
  "crewai_status": "operational",
  "agent_creation": "success",
  "framework_version": "0.1.0"
}
```

## 👥 Teams API

### Create Team

```http
POST /api/v1/teams/
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Product Development Team",
  "description": "AI team for product strategy and development",
  "monthly_budget": 500.00,
  "roles": [
    {
      "title": "Product Manager",
      "description": "Strategic product planning and roadmap",
      "expertise": "senior",
      "llm_model": "gpt-4",
      "llm_config": {
        "temperature": 0.7,
        "max_tokens": 2000
      },
      "agent_config": {
        "backstory": "Expert product manager with 10+ years experience",
        "goals": ["Define product strategy", "Analyze market trends"],
        "tools": ["market_research", "analytics"]
      },
      "is_active": true
    },
    {
      "title": "Software Developer",
      "description": "Full-stack development and architecture",
      "expertise": "intermediate",
      "llm_model": "gpt-3.5-turbo",
      "is_active": true
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "auth_owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Product Development Team",
  "description": "AI team for product strategy and development",
  "monthly_budget": "500.00",
  "current_spend": "0.00",
  "status": "idle",
  "last_executed_at": null,
  "created_at": "2025-01-27T13:16:25.292087",
  "updated_at": "2025-01-27T13:16:25.292095",
  "roles": [
    {
      "id": 456,
      "team_id": 123,
      "title": "Product Manager",
      "description": "Strategic product planning and roadmap",
      "expertise": "senior",
      "llm_model": "gpt-4",
      "llm_config": {
        "temperature": 0.7,
        "max_tokens": 2000
      },
      "agent_config": {
        "backstory": "Expert product manager with 10+ years experience",
        "goals": ["Define product strategy", "Analyze market trends"],
        "tools": ["market_research", "analytics"]
      },
      "is_active": true,
      "created_at": "2025-01-27T13:16:25.327969",
      "updated_at": "2025-01-27T13:16:25.327969"
    }
  ]
}
```

### List Teams

```http
GET /api/v1/teams/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "name": "Product Development Team",
    "description": "AI team for product strategy and development",
    "monthly_budget": "500.00",
    "current_spend": "45.75",
    "status": "idle",
    "last_executed_at": "2025-01-27T10:30:00",
    "created_at": "2025-01-27T13:16:25.292087",
    "updated_at": "2025-01-27T13:16:25.292095",
    "roles": []
  }
]
```

### Get Team Details

```http
GET /api/v1/teams/{team_id}
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 123,
  "auth_owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Product Development Team",
  "description": "AI team for product strategy and development",
  "monthly_budget": "500.00",
  "current_spend": "45.75",
  "status": "idle",
  "last_executed_at": "2025-01-27T10:30:00",
  "created_at": "2025-01-27T13:16:25.292087",
  "updated_at": "2025-01-27T13:16:25.292095",
  "roles": [
    {
      "id": 456,
      "team_id": 123,
      "title": "Product Manager",
      "description": "Strategic product planning and roadmap",
      "expertise": "senior",
      "llm_model": "gpt-4",
      "is_active": true,
      "created_at": "2025-01-27T13:16:25.327969"
    }
  ]
}
```

### Update Team

```http
PUT /api/v1/teams/{team_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Product Team",
  "description": "Enhanced team description",
  "monthly_budget": 750.00
}
```

**Response (200 OK):**
```json
{
  "id": 123,
  "name": "Updated Product Team",
  "description": "Enhanced team description",
  "monthly_budget": "750.00",
  "current_spend": "45.75",
  "status": "idle",
  "updated_at": "2025-01-27T14:20:10.123456"
}
```

### Delete Team

```http
DELETE /api/v1/teams/{team_id}
Authorization: Bearer <token>
```

**Response (204 No Content)**

### Get Team Status

```http
GET /api/v1/teams/{team_id}/status
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "team_id": 123,
  "name": "Product Development Team",
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
```

### Execute Team

```http
POST /api/v1/teams/{team_id}/execute
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "inputs": {
    "project_description": "Build a mobile app for food delivery",
    "timeline": "3 months",
    "budget": 50000,
    "target_audience": "Urban millennials",
    "platform": "iOS and Android"
  },
  "execution_config": {
    "max_iterations": 5,
    "timeout_minutes": 30,
    "quality_preference": "balanced"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "team_execution_id": 789,
  "result": "## Product Development Plan\n\n### Executive Summary\nWe've developed a comprehensive plan for a food delivery mobile app targeting urban millennials...",
  "metrics": {
    "execution_time_seconds": 245.7,
    "total_tokens_used": 8750,
    "total_cost": 12.45,
    "tasks_completed": 8,
    "agents_involved": 2
  },
  "breakdown": [
    {
      "role": "Product Manager",
      "task": "Market Analysis",
      "tokens_used": 2500,
      "cost": 3.75,
      "duration_seconds": 89.2
    },
    {
      "role": "Software Developer", 
      "task": "Technical Architecture",
      "tokens_used": 6250,
      "cost": 8.70,
      "duration_seconds": 156.5
    }
  ],
  "started_at": "2025-01-27T15:00:00",
  "completed_at": "2025-01-27T15:04:05"
}
```

### Get Available Models

```http
GET /api/v1/teams/models/available
```

**Response (200 OK):**
```json
{
  "ollama_models": [
    {
      "name": "mistral:7b-instruct",
      "size": "4.1GB", 
      "status": "available",
      "cost_per_token": 0.0,
      "description": "7B parameter instruction-tuned model, great for general tasks"
    },
    {
      "name": "deepseek-coder:6.7b",
      "size": "3.8GB",
      "status": "available", 
      "cost_per_token": 0.0,
      "description": "Specialized coding model"
    }
  ],
  "openai_models": [
    {
      "name": "gpt-3.5-turbo",
      "cost_per_1k_tokens": 0.0015,
      "context_length": 4096,
      "description": "Fast and efficient for most tasks"
    },
    {
      "name": "gpt-4",
      "cost_per_1k_tokens": 0.03,
      "context_length": 8192,
      "description": "Most capable model for complex reasoning"
    }
  ],
  "anthropic_models": [
    {
      "name": "claude-3-haiku",
      "cost_per_1k_tokens": 0.00025,
      "context_length": 200000,
      "description": "Fast and cost-effective"
    },
    {
      "name": "claude-3-sonnet",
      "cost_per_1k_tokens": 0.003,
      "context_length": 200000,
      "description": "Balanced performance and cost"
    }
  ]
}
```

### Get Team Templates

```http
GET /api/v1/teams/templates/available
```

**Response (200 OK):**
```json
[
  {
    "id": "product_development",
    "name": "Product Development Team",
    "description": "Complete product strategy and development team",
    "estimated_monthly_cost": 300,
    "roles": [
      {
        "title": "Product Manager",
        "expertise": "senior",
        "llm_model": "gpt-4",
        "description": "Strategic planning and market analysis"
      },
      {
        "title": "UX Designer", 
        "expertise": "intermediate",
        "llm_model": "gpt-3.5-turbo",
        "description": "User experience and interface design"
      }
    ]
  },
  {
    "id": "content_creation",
    "name": "Content Creation Team",
    "description": "Marketing content and copywriting team",
    "estimated_monthly_cost": 150,
    "roles": [
      {
        "title": "Content Strategist",
        "expertise": "senior", 
        "llm_model": "claude-3-sonnet",
        "description": "Content strategy and planning"
      }
    ]
  }
]
```

## 📊 Data Models

### Team Model

```typescript
interface Team {
  id: number;
  auth_owner_id: string;  // UUID from Supabase
  owner_id?: number;      // Legacy field
  name: string;           // max 100 chars
  description?: string;   // max 1000 chars  
  monthly_budget: string; // Decimal as string
  current_spend: string;  // Decimal as string
  status: TeamStatus;
  last_executed_at?: string; // ISO datetime
  created_at: string;     // ISO datetime
  updated_at: string;     // ISO datetime
  roles: Role[];          // Related roles
}
```

### Role Model

```typescript
interface Role {
  id: number;
  team_id: number;
  title: string;          // max 100 chars
  description?: string;   // max 500 chars
  expertise: ExpertiseLevel;
  llm_model: string;      // max 50 chars
  llm_config?: object;    // Model parameters
  agent_config?: object;  // CrewAI agent config
  is_active: boolean;
  created_at: string;     // ISO datetime
  updated_at: string;     // ISO datetime
}
```

### Execution Models

```typescript
interface TeamExecution {
  id: number;
  team_id: number;
  status: string;
  result?: string;
  error_message?: string;
  execution_metadata?: object;
  tokens_used: number;
  cost: string;           // Decimal as string
  duration_seconds?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
}

interface TaskExecution {
  id: number;
  team_execution_id: number;
  role_id: number;
  task_name: string;
  task_description?: string;
  status: string;
  input_data?: object;
  output_data?: object;
  error_message?: string;
  tokens_used: number;
  cost: string;
  duration_seconds?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
}
```

### Enums

```typescript
enum TeamStatus {
  IDLE = "IDLE",
  RUNNING = "RUNNING", 
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

enum ExpertiseLevel {
  JUNIOR = "junior",
  INTERMEDIATE = "intermediate",
  SENIOR = "senior",
  EXPERT = "expert"
}
```

## 🚨 Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation errors)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "detail": "Error message or validation details",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-27T13:16:25.292087"
}
```

### Common Error Examples

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "monthly_budget"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN"
}
```

**Rate Limit Error (429):**
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## 📈 Rate Limiting

- **Development**: 10,000 requests/minute per IP
- **Production**: 100 requests/minute per user
- **Headers**: Rate limit info in response headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643723400
```

## 🔒 Security Headers

All responses include security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY  
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'...
```

## 🧪 Testing & Development

### Environment Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd workforce_api

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Configure environment
cp env.template .env
# Edit .env with your settings

# 4. Run development server
uvicorn workforce_api.main:app --reload --port 8000
```

### Testing with curl

```bash
# Health check
curl http://localhost:8000/health/ping

# Create team (with dummy auth)
curl -X POST http://localhost:8000/api/v1/teams/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Team",
    "monthly_budget": 100,
    "roles": [
      {
        "title": "Tester",
        "expertise": "intermediate", 
        "llm_model": "gpt-3.5-turbo"
      }
    ]
  }'
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Supabase  
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx

# LLM Providers
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=xxx

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct

# App Config
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📋 Example Workflows

### Basic Team Creation Flow

```javascript
// 1. Create team with roles
const team = await fetch('/api/v1/teams/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: "Marketing Team",
    monthly_budget: 200,
    roles: [
      {
        title: "Content Writer",
        expertise: "intermediate",
        llm_model: "gpt-3.5-turbo"
      }
    ]
  })
})

// 2. Execute team task
const execution = await fetch(`/api/v1/teams/${team.id}/execute`, {
  method: 'POST', 
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    inputs: {
      campaign_topic: "Sustainable Fashion",
      target_audience: "Eco-conscious millennials",
      content_type: "Blog post"
    }
  })
})

// 3. Check execution status
const status = await fetch(`/api/v1/teams/${team.id}/status`, {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### Budget Monitoring Flow

```javascript
// Monitor team spending
const checkBudget = async (teamId) => {
  const status = await fetch(`/api/v1/teams/${teamId}/status`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  
  const { budget_utilization, current_spend, monthly_budget } = await status.json()
  
  if (budget_utilization > 80) {
    console.warn(`Team ${teamId} has used ${budget_utilization}% of budget`)
  }
  
  return {
    spent: current_spend,
    remaining: monthly_budget - current_spend,
    utilization: budget_utilization
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Documentation**: [/docs](http://localhost:8000/docs)
- **GitHub Issues**: [Repository Issues](https://github.com/nuiflo/workforce/issues)
- **Email**: team@nuiflo.com
- **Discord**: [NuiFlo Community](https://discord.gg/nuiflo)

---

**Built with ❤️ by NuiFlo Team** | [MIT License](LICENSE) | [GitHub](https://github.com/nuiflo/workforce)