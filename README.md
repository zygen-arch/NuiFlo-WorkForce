# NuiFlo WorkForce 🚀

**AI-Powered Virtual Team Management Platform**

A SaaS platform for managing virtual teams of AI agents using CrewAI, with support for multiple LLM providers including local Ollama models.

## 🏗️ **Architecture**

- **Backend**: FastAPI + Python (Deployed on VPS)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI Framework**: CrewAI
- **LLM Providers**: OpenAI, Anthropic, Ollama (Local)
- **Frontend**: React + TypeScript (Separate repo)
- **Deployment**: Docker + Nginx + HTTPS

## 🚀 **Quick Start**

### **Backend API**
```bash
# Clone the repository
git clone <repo-url>
cd NuiFlo-WorkForce

# Set up environment
cp env.template .env
# Edit .env with your API keys

# Deploy to VPS
./deploy-vps.sh
```

### **API Endpoints**
- `GET /health/ping` - Basic health check
- `GET /health/ollama-test` - Test Ollama connectivity
- `GET /health/crewai-test` - Test CrewAI integration
- `GET /api/v1/teams/` - List teams
- `POST /api/v1/teams/` - Create team
- `GET /api/v1/teams/models/available` - Available LLM models
- `GET /api/v1/teams/templates/available` - Team templates

## 🎯 **Features**

### **Phase 1: Core Platform (MVP)**
- ✅ Team Builder Wizard
- ✅ Agent Role Configuration
- ✅ Model Router (Ollama + API providers)
- ✅ Basic Dashboard
- ✅ Team Storage (Supabase)
- ✅ Agent Instantiation (CrewAI)

### **Phase 2: Vision-to-Team Chatflow** (Planned)
- Chat UI for natural language team creation
- AI-powered team suggestions
- Template-based team deployment

### **Phase 3: Agentic Collaboration** (Planned)
- @mention system for agent activation
- Real-time agent collaboration
- Task dependency tracking

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://...

# Supabase
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# LLM Providers
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Ollama (Local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# App Settings
ENVIRONMENT=production
CORS_ORIGINS=https://nuiflo.com,https://*.vercel.app
```

## 📁 **Project Structure**

```
NuiFlo-WorkForce/
├── workforce_api/           # FastAPI backend
│   ├── workforce_api/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, auth, database
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── Dockerfile.api      # Docker configuration
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Container orchestration
├── deploy-vps.sh          # Deployment script
├── VPS_DEPLOYMENT_GUIDE.md # Deployment instructions
└── env.template           # Environment template
```

## 🧪 **Testing**

### **Health Checks**
```bash
# Test API health
curl https://api.nuiflo.com/health/ping

# Test Ollama integration
curl https://api.nuiflo.com/health/ollama-test

# Test CrewAI integration
curl https://api.nuiflo.com/health/crewai-test
```

### **Team Management**
```bash
# Get available models
curl https://api.nuiflo.com/api/v1/teams/models/available

# Get team templates
curl https://api.nuiflo.com/api/v1/teams/templates/available

# Create a team (with auth token)
curl -X POST https://api.nuiflo.com/api/v1/teams/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Team", "monthly_budget": 100}'
```

## 🚀 **Deployment**

### **VPS Deployment**
1. **Prerequisites**: Ubuntu VPS with Docker
2. **Ollama Setup**: Install and configure Ollama
3. **Deploy API**: Use `./deploy-vps.sh`
4. **Configure Nginx**: Reverse proxy with HTTPS
5. **Domain Setup**: Point `api.nuiflo.com` to VPS

### **Environment Setup**
- Copy `env.template` to `.env`
- Configure all required environment variables
- Ensure Ollama is running with desired models

## 📊 **Current Status**

- ✅ **Backend API**: Deployed and running
- ✅ **Authentication**: Supabase integration working
- ✅ **Ollama Integration**: Local models responding
- ✅ **CrewAI**: Agent orchestration ready
- ✅ **HTTPS**: Secure communication enabled
- 🔄 **Frontend**: In development (separate repo)
- 🔄 **Phase 1**: Core features implemented

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using CrewAI, FastAPI, and Supabase**
