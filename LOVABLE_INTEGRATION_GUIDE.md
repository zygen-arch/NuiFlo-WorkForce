# NuiFlo WorkForce API - Frontend Integration Guide for Lovable

## 🚀 **API Ready for Frontend Integration**

The NuiFlo WorkForce backend API is **live and operational**, ready for frontend development.

---

## 📡 **API Base Information**

**Live API URL**: `https://nuiflo-workforce.onrender.com`

**Interactive Documentation**: 
- Swagger UI: https://nuiflo-workforce.onrender.com/docs
- OpenAPI JSON: https://nuiflo-workforce.onrender.com/openapi.json

**Status**: ✅ Operational (check: https://nuiflo-workforce.onrender.com/health/status)

---

## 🛠️ **Core API Endpoints**

### **Team Management**
```
POST /api/v1/teams/           # Create new team
GET  /api/v1/teams/           # List all teams  
GET  /api/v1/teams/{id}       # Get specific team
PUT  /api/v1/teams/{id}       # Update team
DELETE /api/v1/teams/{id}     # Delete team
```

### **Team Operations**
```
GET  /api/v1/teams/{id}/status    # Get team status & metrics
POST /api/v1/teams/{id}/execute   # Execute AI team workflow
```

### **Health Checks**
```
GET  /health/ping             # Basic health check
GET  /health/status           # Detailed system status
```

---

## 📋 **TypeScript Data Models**

### **Create Team Request**
```typescript
interface TeamCreate {
  name: string;
  description?: string;
  monthly_budget: number;
  roles: RoleCreate[];
}

interface RoleCreate {
  title: string;
  expertise: "junior" | "intermediate" | "senior" | "expert";
  llm_model: string;           // "gpt-4", "gpt-3.5-turbo", etc.
  description?: string;
  is_active?: boolean;         // defaults to true
}
```

### **Team Response**
```typescript
interface Team {
  id: number;
  owner_id: number;
  name: string;
  description?: string;
  monthly_budget: string;      // Decimal as string (e.g., "500.00")
  current_spend: string;       // Decimal as string (e.g., "45.50")
  status: "idle" | "running" | "paused" | "completed" | "failed";
  last_executed_at?: string;   // ISO datetime string
  created_at: string;          // ISO datetime string
  updated_at: string;          // ISO datetime string
  roles: Role[];
}

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

### **Team Status Response**
```typescript
interface TeamStatus {
  team_id: number;
  name: string;
  status: string;
  monthly_budget: number;
  current_spend: number;
  budget_utilization: number;   // Percentage (0-100)
  last_executed_at?: string;
  role_count: number;
  active_roles: number;
}
```

### **Execution Response**
```typescript
interface ExecutionResponse {
  result?: string;
  metrics: {
    execution_time?: number;
    tokens_used?: number;
    cost?: number;
  };
  success: boolean;
  error?: string;
  team_execution_id?: number;
}
```

---

## 🔧 **API Usage Examples**

### **Create a Team**
```javascript
const createTeam = async (teamData) => {
  const response = await fetch('https://nuiflo-workforce.onrender.com/api/v1/teams/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: "Product Development Team",
      description: "AI team for building mobile apps",
      monthly_budget: 750.00,
      roles: [
        {
          title: "Product Manager",
          expertise: "senior",
          llm_model: "gpt-4"
        },
        {
          title: "Developer", 
          expertise: "intermediate",
          llm_model: "gpt-3.5-turbo"
        }
      ]
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};
```

### **List All Teams**
```javascript
const getTeams = async () => {
  const response = await fetch('https://nuiflo-workforce.onrender.com/api/v1/teams/');
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};
```

### **Get Team Status**
```javascript
const getTeamStatus = async (teamId) => {
  const response = await fetch(`https://nuiflo-workforce.onrender.com/api/v1/teams/${teamId}/status`);
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};
```

### **Execute Team**
```javascript
const executeTeam = async (teamId, inputs = {}) => {
  const response = await fetch(`https://nuiflo-workforce.onrender.com/api/v1/teams/${teamId}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      inputs: {
        project_description: "Build a food delivery mobile app",
        timeline: "3 months",
        budget: 50000,
        ...inputs
      }
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};
```

---

## 🎨 **Recommended UI Components**

### **1. Team Builder (Primary Interface)**
- **Team Name Input**: Text field with validation
- **Description**: Optional textarea
- **Monthly Budget**: Number input with currency formatting and slider
- **Role Builder Section**:
  - Dynamic add/remove role functionality
  - Role title: Text input or dropdown with common roles
  - Expertise level: Radio buttons or dropdown (junior/intermediate/senior/expert)
  - LLM model: Dropdown with options (gpt-4, gpt-3.5-turbo, claude-3, etc.)
  - Role description: Optional textarea

### **2. Team Dashboard**
- **Team Cards/Table**: Display all teams with key info
- **Status Badges**: Color-coded status indicators
- **Budget Visualization**: Progress bars showing budget utilization
- **Quick Actions**: Edit, delete, execute buttons
- **Metrics Display**: Role count, last execution, spending

### **3. Team Execution Interface**
- **Execute Button**: Primary action with loading states
- **Input Form**: Dynamic inputs based on team composition
- **Progress Indicator**: Real-time execution status
- **Results Display**: Formatted output with syntax highlighting
- **Cost Tracking**: Live cost updates during execution

### **4. Team Detail View**
- **Team Overview**: Name, description, status, budget
- **Role Management**: Add/edit/remove roles
- **Execution History**: Past executions with results
- **Settings**: Team configuration options

---

## 🛡️ **Error Handling**

### **HTTP Status Codes**
- `200`: Success
- `201`: Created (for POST requests)
- `204`: No Content (for DELETE requests)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `422`: Unprocessable Entity (Pydantic validation errors)
- `500`: Internal Server Error

### **Error Response Format**
```typescript
interface ErrorResponse {
  detail: string | ValidationError[];
}

interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
```

### **Example Error Handling**
```javascript
const handleApiCall = async (apiCall) => {
  try {
    const result = await apiCall();
    return { success: true, data: result };
  } catch (error) {
    console.error('API Error:', error);
    return { 
      success: false, 
      error: error.message || 'An unexpected error occurred' 
    };
  }
};
```

---

## 🔐 **Authentication & Security**

**Current State**: Dummy authentication (all teams use `user_id=1`)
**Future**: JWT token-based authentication will be implemented

**CORS**: Enabled for common frontend domains (Vercel, Netlify, localhost)

---

## 🚀 **TypeScript Client Generation**

Generate a TypeScript client from the OpenAPI specification:

```bash
npx @openapitools/openapi-generator-cli generate \
  -i https://nuiflo-workforce.onrender.com/openapi.json \
  -g typescript-fetch \
  -o ./src/api/generated
```

This creates type-safe API client functions for all endpoints.

---

## 🎯 **MVP Features to Implement**

### **Phase 1: Core Team Management**
1. ✅ Team creation form with role builder
2. ✅ Team listing/dashboard view
3. ✅ Team detail/edit view
4. ✅ Basic team execution

### **Phase 2: Enhanced UX**
1. Real-time execution progress
2. Advanced role templates
3. Budget optimization suggestions
4. Team performance analytics

### **Phase 3: Advanced Features**
1. Multi-team projects
2. Team collaboration tools
3. Custom workflow builders
4. Integration marketplace

---

## 📞 **Support & Resources**

- **Live API Testing**: https://nuiflo-workforce.onrender.com/docs
- **Health Check**: https://nuiflo-workforce.onrender.com/health/status
- **Repository**: GitHub repo with full documentation
- **Backend Status**: Deployed on Render with auto-scaling

---

## 🎉 **Get Started**

1. **Test the API**: Visit the Swagger UI to explore all endpoints
2. **Create a test team**: Use the POST /api/v1/teams/ endpoint
3. **Build the team builder**: Start with the core team creation form
4. **Integrate execution**: Add team execution functionality
5. **Enhance UX**: Add real-time features and advanced visualizations

**The backend is production-ready and waiting for your frontend magic!** 🚀

---

*Generated for NuiFlo WorkForce API v0.1.0 - AI Team Management Platform* 