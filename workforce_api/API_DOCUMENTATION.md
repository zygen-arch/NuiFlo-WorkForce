# NuiFlo WorkForce API Documentation

AI Team Management Platform powered by CrewAI

**Base URL**: `http://localhost:8000`  
**API Version**: `0.1.0`

## 📚 Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) 
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## 🔧 Quick Setup for Frontend

1. **Development Server**: `http://localhost:8000`
2. **CORS**: Enabled for `http://localhost:5173` (Vite) and `http://localhost:3000` (React)
3. **Authentication**: Currently dummy (user_id=1) - production auth coming soon

## 🚀 Core API Endpoints

### Health Check
```http
GET /health/ping
GET /health/status
```

### Teams Management

#### Create Team
```http
POST /api/v1/teams/
Content-Type: application/json

{
  "name": "My AI Team",
  "description": "A team for product development",
  "monthly_budget": 500.00,
  "roles": [
    {
      "title": "Product Manager",
      "expertise": "senior",
      "llm_model": "gpt-4"
    },
    {
      "title": "Developer",
      "expertise": "intermediate", 
      "llm_model": "gpt-3.5-turbo"
    }
  ]
}
```

**Response**:
```json
{
  "id": 1,
  "owner_id": 1,
  "name": "My AI Team",
  "description": "A team for product development", 
  "monthly_budget": "500.00",
  "current_spend": "0.00",
  "status": "idle",
  "last_executed_at": null,
  "created_at": "2025-07-27T13:16:25.292087",
  "updated_at": "2025-07-27T13:16:25.292095",
  "roles": [
    {
      "id": 1,
      "team_id": 1,
      "title": "Product Manager",
      "expertise": "senior",
      "llm_model": "gpt-4",
      "is_active": true,
      "created_at": "2025-07-27T13:16:25.327969"
    }
  ]
}
```

#### List Teams
```http
GET /api/v1/teams/
```

#### Get Team Details
```http
GET /api/v1/teams/{team_id}
```

#### Update Team
```http
PUT /api/v1/teams/{team_id}
Content-Type: application/json

{
  "name": "Updated Team Name",
  "monthly_budget": 750.00
}
```

#### Delete Team
```http
DELETE /api/v1/teams/{team_id}
```

#### Get Team Status
```http
GET /api/v1/teams/{team_id}/status
```

**Response**:
```json
{
  "team_id": 1,
  "name": "My AI Team",
  "status": "idle",
  "monthly_budget": 500.0,
  "current_spend": 0.0,
  "budget_utilization": 0.0,
  "last_executed_at": null,
  "role_count": 2,
  "active_roles": 2
}
```

#### Execute Team (CrewAI)
```http
POST /api/v1/teams/{team_id}/execute
Content-Type: application/json

{
  "inputs": {
    "project_description": "Build a mobile app for food delivery",
    "timeline": "3 months",
    "budget": 50000
  }
}
```

**Response**:
```json
{
  "result": "Team execution completed successfully",
  "metrics": {
    "execution_time": 45.2,
    "tokens_used": 1250,
    "cost": 2.35
  },
  "success": true,
  "error": null,
  "team_execution_id": 123
}
```

## 📊 Data Models

### ExpertiseLevel (Enum)
- `junior`
- `intermediate` 
- `senior`
- `expert`

### TeamStatus (Enum)
- `idle`
- `running`
- `paused`
- `completed`
- `failed`

### Role Object
```typescript
interface Role {
  id: number;
  team_id: number;
  title: string;
  description?: string;
  expertise: "junior" | "intermediate" | "senior" | "expert";
  llm_model: string;
  llm_config?: object;
  agent_config?: object;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### Team Object
```typescript
interface Team {
  id: number;
  owner_id: number;
  name: string;
  description?: string;
  monthly_budget: string;
  current_spend: string;
  status: "idle" | "running" | "paused" | "completed" | "failed";
  last_executed_at?: string;
  created_at: string;
  updated_at: string;
  roles: Role[];
}
```

## 🔍 Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content (for deletes)
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message or validation details"
}
```

## 💡 Frontend Integration Tips

### 1. TypeScript Client Generation
Use the OpenAPI spec to generate TypeScript clients:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o ./src/api
```

### 2. React Hook Example
```typescript
import { useState, useEffect } from 'react';

interface Team {
  id: number;
  name: string;
  status: string;
  monthly_budget: string;
  roles: Role[];
}

export function useTeams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/teams/')
      .then(res => res.json())
      .then(data => {
        setTeams(data);
        setLoading(false);
      });
  }, []);

  const createTeam = async (teamData: any) => {
    const response = await fetch('http://localhost:8000/api/v1/teams/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(teamData)
    });
    return response.json();
  };

  return { teams, loading, createTeam };
}
```

### 3. State Management (Zustand/Redux)
```typescript
interface TeamStore {
  teams: Team[];
  selectedTeam: Team | null;
  loading: boolean;
  fetchTeams: () => Promise<void>;
  createTeam: (data: TeamCreate) => Promise<Team>;
  executeTeam: (id: number, inputs?: object) => Promise<ExecutionResult>;
}
```

## 🔐 Authentication (Future)

Current API uses dummy authentication. Production will implement:
- JWT tokens
- User registration/login
- Protected routes
- Role-based access control

## 📈 Rate Limiting & Performance

- No rate limiting in development
- Recommended: 100 requests/minute per user in production
- Database connection pooling enabled
- CORS configured for frontend domains

## 🐛 Development & Debugging

### Database Status
```http
GET /health/status
```

### Logs
Server logs show detailed SQL queries and execution traces when `DEBUG=true`.

### Testing Endpoints
Use the provided Swagger UI at `/docs` for interactive testing.

---

**Need Help?** 
- Check the interactive docs at `/docs`
- Review the OpenAPI spec at `/openapi.json`
- Contact: team@nuiflo.com 