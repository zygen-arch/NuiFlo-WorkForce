# NuiFlo WorkForce API - Frontend Integration Guide

## 🚀 Quick Start for Lovable Frontend Team

### Backend Status: ✅ READY FOR INTEGRATION

The NuiFlo WorkForce backend API is **fully operational** and ready for frontend integration.

## 📡 API Endpoints

**Base URL**: `http://localhost:8000`

### Key Endpoints for Frontend:
```
POST /api/v1/teams/           # Create new team
GET  /api/v1/teams/           # List user teams  
GET  /api/v1/teams/{id}       # Get team details
GET  /api/v1/teams/{id}/status # Team status & metrics
POST /api/v1/teams/{id}/execute # Execute AI team
PUT  /api/v1/teams/{id}       # Update team
DELETE /api/v1/teams/{id}     # Delete team
```

## 📋 Core Data Structure

### Team Creation Payload:
```typescript
interface TeamCreate {
  name: string;
  description?: string;
  monthly_budget: number;
  roles: Array<{
    title: string;
    expertise: "junior" | "intermediate" | "senior" | "expert";
    llm_model: string;
    description?: string;
  }>;
}
```

### Team Response:
```typescript
interface Team {
  id: number;
  name: string;
  status: "idle" | "running" | "paused" | "completed" | "failed";
  monthly_budget: string;
  current_spend: string;
  roles: Role[];
  created_at: string;
  // ... other fields
}
```

## 🔗 Documentation & Specs

1. **Interactive Swagger UI**: http://localhost:8000/docs
2. **OpenAPI JSON Spec**: `./workforce_api_openapi.json` 
3. **Full API Docs**: `./workforce_api/API_DOCUMENTATION.md`

## 🛠️ TypeScript Client Generation

```bash
# Generate TypeScript client from OpenAPI spec
npx @openapitools/openapi-generator-cli generate \
  -i ./workforce_api_openapi.json \
  -g typescript-fetch \
  -o ./src/api
```

## 🎯 MVP Frontend Requirements

### Team Builder Interface:
1. **Team Creation Form**:
   - Team name input
   - Description textarea  
   - Monthly budget slider/input
   - Add/remove roles dynamically
   - Role configuration (title, expertise, LLM model)

2. **Team Dashboard**:
   - List all teams
   - Show team status badges
   - Budget utilization bars
   - Quick actions (edit, delete, execute)

3. **Team Execution**:
   - Execute button with inputs form
   - Real-time status updates
   - Results display

## ✅ Backend Features Working:

- [x] Database (Supabase PostgreSQL)
- [x] Team CRUD operations  
- [x] Role management
- [x] Budget tracking
- [x] CrewAI execution framework
- [x] CORS configured for frontend
- [x] Comprehensive error handling
- [x] OpenAPI documentation

## 🔄 API Usage Examples

### Create Team:
```javascript
const team = await fetch('http://localhost:8000/api/v1/teams/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Product Development Team",
    monthly_budget: 500.00,
    roles: [
      { title: "Product Manager", expertise: "senior", llm_model: "gpt-4" },
      { title: "Developer", expertise: "intermediate", llm_model: "gpt-3.5-turbo" }
    ]
  })
});
```

### Get Teams:
```javascript
const teams = await fetch('http://localhost:8000/api/v1/teams/')
  .then(res => res.json());
```

### Execute Team:
```javascript
const result = await fetch(`http://localhost:8000/api/v1/teams/${teamId}/execute`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    inputs: {
      project_description: "Build a mobile app",
      timeline: "3 months"
    }
  })
});
```

## 🎨 UI/UX Recommendations

### Team Builder Form:
- Step-by-step wizard (Team Info → Roles → Budget → Review)
- Drag-and-drop role reordering
- Real-time budget calculator
- LLM model selection with cost indicators

### Dashboard:
- Card-based team layout
- Status indicators with colors
- Budget progress bars
- Quick action buttons

### Execution View:
- Progress indicators
- Streaming results display
- Cost tracking in real-time
- Export/save results

## 🔐 Authentication Note

Currently using **dummy authentication** (user_id=1). All teams are associated with this user. Production authentication will be implemented later.

## 🌐 CORS & Development

CORS is configured for:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)

## 📞 Support

- **Full API Documentation**: See `API_DOCUMENTATION.md`
- **OpenAPI Spec**: Use `workforce_api_openapi.json`
- **Interactive Testing**: http://localhost:8000/docs
- **Backend Status**: http://localhost:8000/health/status

---

**Ready to build! 🚀** The backend is stable, documented, and waiting for your frontend magic! 