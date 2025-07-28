# 🚀 **NuiFlo WorkForce API - Frontend Integration Guide**

## 🚨 **CRITICAL SECURITY UPDATE (2025-01-27)**

**AUTHENTICATION IS NOW REQUIRED FOR ALL API ENDPOINTS!** 🔐

All API endpoints now require valid Supabase JWT tokens. **Unauthenticated requests will receive 401 Unauthorized.**

### **Security Features Now Active:**
✅ **JWT Authentication**: All endpoints require `Authorization: Bearer <token>`  
✅ **Ownership Validation**: Users can only access their own teams/data  
✅ **RLS Security**: Database enforces row-level security policies  
✅ **Proper Error Responses**: 401 Unauthorized, 403 Forbidden as needed  

---

## 📋 **Production-Ready Backend Status**

✅ **API Deployed**: `https://nuiflo-workforce.onrender.com`  
✅ **Database**: Supabase PostgreSQL with RLS security  
✅ **Authentication**: Supabase Auth integration **ACTIVE & REQUIRED**  
✅ **Auto Profile Creation**: SQL trigger creates profiles on signup  
✅ **CORS**: Configured for all frontend URLs  
✅ **Documentation**: Full OpenAPI/Swagger at `/docs`  

---

## 🔐 **Authentication Setup**

### **Supabase Configuration Required:**
```javascript
// Frontend needs these environment variables
VITE_SUPABASE_URL=https://pyuwxaocmnbaipqjdlrv.supabase.co
VITE_SUPABASE_ANON_KEY=[GET_FROM_SUPABASE_DASHBOARD]
VITE_API_BASE_URL=https://nuiflo-workforce.onrender.com
```

### **Auth Flow Overview:**
1. **User Signs Up** → Supabase Auth creates user in `auth.users`
2. **Trigger Fires** → Automatically creates profile in `public.profiles` 
3. **User Gets JWT** → Frontend receives Supabase session token
4. **API Calls** → Include `Authorization: Bearer <jwt>` header
5. **RLS Security** → Database ensures users only see their own data

---

## 🛡️ **Security Implementation**

### **Row Level Security (RLS) Active:**
- ✅ Users can only access their own teams, roles, executions
- ✅ All API endpoints protected by auth middleware
- ✅ Database enforces security at the row level
- ✅ No risk of data leakage between users

### **Authentication Headers:**
```javascript
// All API calls must include:
headers: {
  'Authorization': `Bearer ${supabaseSession.access_token}`,
  'Content-Type': 'application/json'
}
```

---

## 🎯 **API Endpoints Ready for Integration**

### **Base URL:** `https://nuiflo-workforce.onrender.com`

**⚠️ IMPORTANT: All endpoints require authentication via `Authorization: Bearer <jwt>` header**

### **Health Check:**
```javascript
GET /health/ping
// Returns: {"status": "healthy", "timestamp": "2025-01-27T..."}
// NOTE: This is the ONLY endpoint that doesn't require authentication
```

### **Team Management:**
```javascript
// Create a new AI team
POST /api/v1/teams/
{
  "name": "My Development Team",
  "description": "AI team for product development",
  "monthly_budget": 500.00,
  "roles": [
    {
      "name": "Technical Architect",
      "description": "System design and architecture",
      "expertise_level": "expert",
      "llm_model": "gpt-4"
    },
    {
      "name": "Backend Developer", 
      "description": "API and database development",
      "expertise_level": "senior",
      "llm_model": "gpt-3.5-turbo"
    }
  ]
}

// Get all user's teams
GET /api/v1/teams/

// Get specific team with roles
GET /api/v1/teams/{team_id}/

// Update team
PUT /api/v1/teams/{team_id}/

// Delete team
DELETE /api/v1/teams/{team_id}/

// Get team status & metrics
GET /api/v1/teams/{team_id}/status

// Execute team workflow
POST /api/v1/teams/{team_id}/execute
{
  "input": "Build a REST API for user management",
  "context": {
    "technology": "FastAPI",
    "database": "PostgreSQL"
  }
}
```

---

## 📊 **Data Models**

### **Team Response:**
```typescript
interface TeamResponse {
  id: number;
  name: string;
  description: string | null;
  monthly_budget: number;
  current_spend: number;
  status: "idle" | "running" | "paused" | "completed" | "failed";
  last_executed_at: string | null;
  created_at: string;
  updated_at: string;
  roles: RoleResponse[];
}
```

### **Role Response:**
```typescript
interface RoleResponse {
  id: number;
  name: string;
  description: string;
  expertise_level: "junior" | "mid" | "senior" | "expert";
  llm_model: string;
  created_at: string;
  updated_at: string;
}
```

### **Team Status Response:**
```typescript
interface TeamStatusResponse {
  team: TeamResponse;
  metrics: {
    total_executions: number;
    successful_executions: number;
    failed_executions: number;
    total_tokens_used: number;
    total_cost: number;
    average_execution_time: number | null;
    last_execution_date: string | null;
  };
  recent_executions: ExecutionResponse[];
}
```

---

## 🚀 **Frontend Implementation Guide**

### **1. Install Supabase Client:**
```bash
npm install @supabase/supabase-js
```

### **2. Initialize Supabase:**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_ANON_KEY
)
```

### **3. Authentication Service:**
```javascript
// Sign up user
const signUp = async (email, password, fullName) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name: fullName
      }
    }
  })
  // Profile automatically created by database trigger!
  return { data, error }
}

// Sign in user  
const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })
  return { data, error }
}

// Get current session
const getSession = () => supabase.auth.getSession()

// Sign out
const signOut = () => supabase.auth.signOut()
```

### **4. API Service with Auth:**
```javascript
class APIService {
  constructor() {
    this.baseURL = process.env.VITE_API_BASE_URL
  }

  async getAuthHeaders() {
    const { data: { session } } = await supabase.auth.getSession()
    return {
      'Authorization': `Bearer ${session?.access_token}`,
      'Content-Type': 'application/json'
    }
  }

  async createTeam(teamData) {
    const headers = await this.getAuthHeaders()
    const response = await fetch(`${this.baseURL}/api/v1/teams/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(teamData)
    })
    return response.json()
  }

  async getUserTeams() {
    const headers = await this.getAuthHeaders()
    const response = await fetch(`${this.baseURL}/api/v1/teams/`, {
      method: 'GET',
      headers
    })
    return response.json()
  }

  async executeTeam(teamId, input) {
    const headers = await this.getAuthHeaders()
    const response = await fetch(`${this.baseURL}/api/v1/teams/${teamId}/execute`, {
      method: 'POST', 
      headers,
      body: JSON.stringify({ input })
    })
    return response.json()
  }
}
```

### **5. Protected Route Example:**
```javascript
const ProtectedRoute = ({ children }) => {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  if (loading) return <div>Loading...</div>
  if (!session) return <Navigate to="/login" />
  
  return children
}
```

---

## 🧪 **Testing & Validation**

### **Test Authentication Flow:**
1. **Sign up** with test email → Profile auto-created ✅
2. **Get session token** → Use in API calls ✅  
3. **Create team** → Returns team with roles ✅
4. **List teams** → Shows only user's teams ✅
5. **Execute team** → Returns workflow results ✅

### **Test Security:**
- ✅ Unauthenticated calls return 401
- ✅ Users can't access other users' teams
- ✅ RLS enforces data isolation
- ✅ All sensitive operations require valid JWT

---

## 📖 **API Documentation**

**Full Interactive Documentation:** `https://nuiflo-workforce.onrender.com/docs`

- ✅ **Swagger UI**: Test all endpoints interactively
- ✅ **OpenAPI Schema**: Auto-generated TypeScript types available
- ✅ **Examples**: Request/response examples for all endpoints
- ✅ **Authentication**: Bearer token auth documented

---

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **CORS Errors:** 
   - ✅ Already configured for all Lovable URLs
   - ✅ Supports dynamic origins for development

2. **Authentication Errors:**
   - Verify Supabase URL and anon key
   - Check JWT token in request headers
   - Ensure user is signed in before API calls

3. **404 Errors:**
   - API base URL: `https://nuiflo-workforce.onrender.com`
   - All endpoints prefixed with `/api/v1/`

4. **RLS Permission Denied:**
   - User must be authenticated with valid JWT
   - Check that auth headers are included
   - Verify user owns the resources they're accessing

---

## 🎯 **Integration Checklist**

### **Backend (Complete ✅):**
- [x] API deployed and running
- [x] Database with RLS security
- [x] Supabase Auth integration
- [x] Auto profile creation
- [x] CORS configured
- [x] All endpoints documented

### **Frontend (Your Tasks):**
- [ ] Install and configure Supabase client
- [ ] Implement authentication UI (signup/login)
- [ ] Create protected routes
- [ ] Build team management interface
- [ ] Integrate API calls with auth headers
- [ ] Handle authentication state
- [ ] Test complete user flow

---

## 🚀 **Ready for Production!**

The backend is **production-ready** with:
- 🔒 **Security**: RLS, JWT auth, input validation
- 📈 **Scalability**: Deployed on Render with auto-scaling
- 🛡️ **Reliability**: Error handling, graceful degradation
- 📊 **Monitoring**: Health checks, structured logging
- 🔄 **CI/CD**: Automatic deployments with migrations

**Start building the frontend - the backend is ready to power your AI workforce platform!** 💪 