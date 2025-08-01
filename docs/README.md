# NuiFlo WorkForce - Complete Documentation

## 📚 Documentation Overview

Welcome to the comprehensive documentation for NuiFlo WorkForce, an AI-powered virtual team management platform built with CrewAI, FastAPI, and Supabase.

### 🎯 What is NuiFlo WorkForce?

NuiFlo WorkForce is a SaaS platform that enables you to create, deploy, and manage teams of AI agents using CrewAI. The platform supports multiple LLM providers including local Ollama models, OpenAI, and Anthropic, with intelligent routing for cost optimization and performance.

## 📖 Documentation Structure

### 🚀 Getting Started
- **[Main README](../README.md)** - Project overview and quick start
- **[API Documentation](COMPREHENSIVE_API_DOCUMENTATION.md)** - Complete API reference with examples

### 🏗️ Core System
- **[Core Components](CORE_COMPONENTS_DOCUMENTATION.md)** - Configuration, authentication, database, and intelligent router
- **[Data Models](DATA_MODELS_DOCUMENTATION.md)** - Database models, schemas, relationships, and validation
- **[Services Documentation](SERVICES_DOCUMENTATION.md)** - Business logic, team management, and service patterns

### 🤖 AI Integration
- **[CrewAI Integration](CREWAI_INTEGRATION_DOCUMENTATION.md)** - AI agent orchestration, workflow execution, and advanced patterns

### 🚢 Deployment & Operations
- **[VPS Deployment Guide](../VPS_DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Frontend Integration Guide](../FRONTEND_INTEGRATION_GUIDE.md)** - Frontend development guidelines
- **[Lovable Integration Guide](../LOVABLE_INTEGRATION_GUIDE.md)** - Lovable platform integration

## 🔍 Quick Navigation

### For Developers
| Task | Documentation |
|------|---------------|
| **API Integration** | [API Documentation](COMPREHENSIVE_API_DOCUMENTATION.md) |
| **Understanding Models** | [Data Models](DATA_MODELS_DOCUMENTATION.md) |
| **Business Logic** | [Services Documentation](SERVICES_DOCUMENTATION.md) |
| **Core Components** | [Core Components](CORE_COMPONENTS_DOCUMENTATION.md) |

### For AI/ML Engineers
| Task | Documentation |
|------|---------------|
| **CrewAI Integration** | [CrewAI Documentation](CREWAI_INTEGRATION_DOCUMENTATION.md) |
| **LLM Routing** | [Core Components - Intelligent Router](CORE_COMPONENTS_DOCUMENTATION.md#-intelligent-llm-router) |
| **Agent Configuration** | [CrewAI - NuiFlo Extensions](CREWAI_INTEGRATION_DOCUMENTATION.md#-nuiflo-extensions) |

### For DevOps
| Task | Documentation |
|------|---------------|
| **Production Deployment** | [VPS Deployment Guide](../VPS_DEPLOYMENT_GUIDE.md) |
| **Configuration** | [Core Components - Configuration](CORE_COMPONENTS_DOCUMENTATION.md#-configuration-system) |
| **Health Monitoring** | [API - Health Endpoints](COMPREHENSIVE_API_DOCUMENTATION.md#-health-endpoints) |

### For Frontend Developers
| Task | Documentation |
|------|---------------|
| **API Integration** | [API Documentation](COMPREHENSIVE_API_DOCUMENTATION.md) |
| **Frontend Setup** | [Frontend Integration Guide](../FRONTEND_INTEGRATION_GUIDE.md) |
| **Authentication** | [Core Components - Auth](CORE_COMPONENTS_DOCUMENTATION.md#-authentication--security) |

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NuiFlo WorkForce Platform                    │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React/TypeScript)                                   │
│  ├── Team Builder UI                                           │
│  ├── Execution Dashboard                                       │
│  └── Budget Monitoring                                         │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                          │
│  ├── Teams API (/api/v1/teams/)                               │
│  ├── Health Checks (/health/)                                 │
│  └── Authentication (Supabase JWT)                            │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                         │
│  ├── TeamService (CRUD, execution)                            │
│  ├── CrewAI Extensions (NuiFloAgent, NuiFloTask)             │
│  └── Intelligent LLM Router                                   │
├─────────────────────────────────────────────────────────────────┤
│  Core Components                                              │
│  ├── Configuration (Pydantic Settings)                        │
│  ├── Database (SQLAlchemy + PostgreSQL)                       │
│  ├── Authentication (Supabase Integration)                    │
│  └── Security (Rate Limiting, Input Sanitization)            │
├─────────────────────────────────────────────────────────────────┤
│  AI Integration Layer                                         │
│  ├── CrewAI Framework                                         │
│  ├── Multi-LLM Support (OpenAI, Anthropic, Ollama)          │
│  └── Cost Optimization & Tracking                             │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                    │
│  ├── Supabase (PostgreSQL + Auth)                            │
│  ├── Team & Role Management                                   │
│  └── Execution Tracking & Analytics                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Key Features

### 🎯 Team Management
- **Visual Team Builder** - Create AI teams with custom roles and expertise levels
- **Role Configuration** - Define agent backstories, goals, and LLM preferences
- **Budget Tracking** - Monitor spending and set monthly budget limits
- **Team Templates** - Pre-configured teams for common use cases

### 🧠 Intelligent AI Orchestration
- **Multi-LLM Support** - OpenAI, Anthropic, and local Ollama models
- **Smart Routing** - Automatic model selection based on task complexity
- **Cost Optimization** - Balance quality and cost with intelligent fallbacks
- **Real-time Execution** - Live monitoring of team execution and metrics

### 🔒 Enterprise Features
- **Supabase Authentication** - Secure user management and JWT tokens
- **Role-based Access** - Team ownership and permission management
- **Audit Trails** - Complete execution history and cost tracking
- **API Security** - Rate limiting, input sanitization, and HTTPS

## 📊 API Quick Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health/ping` | Basic health check |
| `GET` | `/health/status` | System status with database connectivity |
| `GET` | `/api/v1/teams/` | List user teams |
| `POST` | `/api/v1/teams/` | Create new team |
| `GET` | `/api/v1/teams/{id}` | Get team details |
| `PUT` | `/api/v1/teams/{id}` | Update team |
| `DELETE` | `/api/v1/teams/{id}` | Delete team |
| `GET` | `/api/v1/teams/{id}/status` | Get team status and metrics |
| `POST` | `/api/v1/teams/{id}/execute` | Execute team with CrewAI |

### Authentication
All endpoints (except health checks) require authentication:
```http
Authorization: Bearer <supabase_jwt_token>
```

### Example Usage
```bash
# Create a team
curl -X POST https://api.nuiflo.com/api/v1/teams/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing Team",
    "monthly_budget": 500,
    "roles": [
      {
        "title": "Content Strategist",
        "expertise": "senior",
        "llm_model": "gpt-4"
      }
    ]
  }'

# Execute team
curl -X POST https://api.nuiflo.com/api/v1/teams/123/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "project_description": "Launch a sustainable fashion brand",
      "target_audience": "Eco-conscious millennials",
      "budget": 50000
    }
  }'
```

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or Supabase account)
- Node.js 18+ (for frontend)
- Docker (optional, for local development)

### Quick Start
```bash
# 1. Clone repository
git clone <repo-url>
cd nuiflo-workforce

# 2. Backend setup
cd workforce_api
cp env.template .env
# Edit .env with your configuration

pip install -r requirements.txt
uvicorn workforce_api.main:app --reload

# 3. Frontend setup (separate repository)
# See Frontend Integration Guide

# 4. Access API documentation
open http://localhost:8000/docs
```

### Environment Configuration
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

# Ollama (local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct

# App
ENVIRONMENT=development
DEBUG=true
```

## 🤖 AI Agent Examples

### Basic Team Creation
```python
from workforce_api.services import TeamService
from decimal import Decimal

# Create team with multiple roles
team = TeamService.create_team(
    name="Product Development Team",
    owner_id="user-uuid-from-supabase",
    monthly_budget=Decimal("800.00"),
    description="AI team for product strategy and development",
    roles_data=[
        {
            "title": "Product Manager",
            "expertise": "senior",
            "llm_model": "gpt-4",
            "agent_config": {
                "backstory": "Senior PM with 10+ years experience",
                "goals": ["Define strategy", "Analyze market"],
                "tools": ["market_research", "analytics"]
            }
        },
        {
            "title": "UX Designer",
            "expertise": "intermediate",
            "llm_model": "gpt-3.5-turbo",
            "agent_config": {
                "backstory": "Creative UX designer focused on user experience",
                "goals": ["Design interfaces", "Improve usability"]
            }
        }
    ]
)
```

### Team Execution with CrewAI
```python
from workforce_api.services.hybrid_crew_extensions import create_hybrid_crew_from_team

# Execute team with intelligent LLM routing
result = await create_hybrid_crew_from_team(
    team=team,
    execution_inputs={
        "project_description": "Build a task management mobile app",
        "target_audience": "Remote teams and freelancers",
        "timeline": "3 months",
        "budget": 75000
    },
    quality_preference="balanced",  # fast/balanced/premium/cost_optimized
    max_budget_per_task=10.0
)

if result["success"]:
    print(f"✅ Execution completed!")
    print(f"💰 Total cost: ${result['total_cost']}")
    print(f"📊 Tasks completed: {result['metrics']['tasks_completed']}")
    print(f"🤖 Agents involved: {result['metrics']['agents_involved']}")
```

## 📈 Monitoring & Analytics

### Team Performance Metrics
- **Execution Success Rate** - Percentage of successful team executions
- **Average Cost per Execution** - Cost efficiency tracking
- **Budget Utilization** - Monthly budget usage monitoring
- **Agent Performance** - Individual role effectiveness metrics

### System Health Monitoring
```bash
# Check system status
curl https://api.nuiflo.com/health/status

# Monitor Ollama connectivity
curl https://api.nuiflo.com/health/ollama-test

# Test CrewAI integration
curl https://api.nuiflo.com/health/crewai-test
```

## 🚀 Deployment Options

### 1. VPS Deployment (Recommended)
- **Full control** over infrastructure
- **Cost-effective** for production use
- **Supports Ollama** for local LLM models
- **See**: [VPS Deployment Guide](../VPS_DEPLOYMENT_GUIDE.md)

### 2. Cloud Platforms
- **Railway** - Simple deployment with PostgreSQL
- **Render** - Easy setup with automatic HTTPS
- **Heroku** - Quick deployment (limited Ollama support)

### 3. Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d

# Access API
open https://localhost:8000/docs
```

## 🔗 Integration Examples

### React Frontend Integration
```typescript
import { useState, useEffect } from 'react'

interface Team {
  id: number
  name: string
  status: string
  monthly_budget: string
  current_spend: string
}

export function useTeams() {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchTeams()
  }, [])
  
  const fetchTeams = async () => {
    const response = await fetch('/api/v1/teams/', {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      }
    })
    
    const data = await response.json()
    setTeams(data)
    setLoading(false)
  }
  
  const createTeam = async (teamData: any) => {
    const response = await fetch('/api/v1/teams/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(teamData)
    })
    
    return response.json()
  }
  
  const executeTeam = async (teamId: number, inputs: any) => {
    const response = await fetch(`/api/v1/teams/${teamId}/execute`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ inputs })
    })
    
    return response.json()
  }
  
  return { teams, loading, createTeam, executeTeam, fetchTeams }
}
```

### Python Client Example
```python
import httpx
from typing import Dict, Any

class NuiFloClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def create_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/teams/",
                headers=self.headers,
                json=team_data
            )
            return response.json()
    
    async def execute_team(self, team_id: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/teams/{team_id}/execute",
                headers=self.headers,
                json={"inputs": inputs}
            )
            return response.json()

# Usage
client = NuiFloClient("https://api.nuiflo.com", "your-token")
result = await client.execute_team(123, {
    "project_description": "Design a new mobile app",
    "budget": 50000
})
```

## 🎓 Learning Resources

### Tutorials
1. **[Getting Started Tutorial](COMPREHENSIVE_API_DOCUMENTATION.md#-example-workflows)** - Basic team creation and execution
2. **[Advanced Patterns](CREWAI_INTEGRATION_DOCUMENTATION.md#-advanced-usage-patterns)** - Multi-team orchestration and iterative refinement
3. **[Cost Optimization](CORE_COMPONENTS_DOCUMENTATION.md#-intelligent-llm-router)** - LLM routing strategies

### Best Practices
- **Team Composition** - How to structure effective AI teams
- **Budget Management** - Optimizing costs while maintaining quality
- **Error Handling** - Robust execution patterns
- **Performance Optimization** - Scaling and monitoring strategies

### Community
- **GitHub Discussions** - Ask questions and share experiences
- **Discord Community** - Real-time chat and support
- **Example Projects** - Sample applications and integrations

## 🔧 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check database status
curl http://localhost:8000/health/status

# Verify DATABASE_URL
echo $DATABASE_URL
```

#### Authentication Problems
```bash
# Test Supabase configuration
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Verify JWT token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/teams/
```

#### Ollama Integration
```bash
# Test Ollama directly
curl http://localhost:11434/api/version

# Check NuiFlo integration
curl http://localhost:8000/health/ollama-test
```

### Support Channels
- **GitHub Issues** - Bug reports and feature requests
- **Documentation** - Comprehensive guides and API reference
- **Community Discord** - Real-time help and discussions
- **Email Support** - team@nuiflo.com

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for API changes
- Use type hints and docstrings

---

**Built with ❤️ by the NuiFlo Team** | [Website](https://nuiflo.com) | [GitHub](https://github.com/nuiflo/workforce) | [Discord](https://discord.gg/nuiflo)