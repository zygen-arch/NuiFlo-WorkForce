# NuiFlo WorkForce - AI Team Management Platform

A comprehensive platform for building, deploying, and managing AI-powered virtual teams using CrewAI.

## 🏗️ Project Structure

```
nuiflo-workforce/
├── backend/                 # FastAPI backend API
│   ├── app/                # Python package (models, services, API)
│   ├── migrations/         # Database migrations
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── test_spaces.py     # Space functionality tests
├── frontend/              # React frontend
│   ├── src/              # React source code
│   ├── components/       # React components
│   └── contexts/         # React contexts
├── docs/                 # Documentation and guides
├── docker-compose.yml    # Full stack orchestration
├── .env                  # Environment variables
└── README.md            # This file
```

## 🚀 Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

### Full Stack (Docker)
```bash
docker-compose up
```

## 📋 Features

### Phase 1: Core Platform (MVP) ✅
- **Team Spaces**: Virtual boundaries for AI agent operations
- **Space Management**: CRUD operations for team spaces
- **Space-Aware Teams**: Teams and roles are space-scoped
- **Space Context**: Frontend state management for spaces
- **Space Selector**: UI for space switching

### Upcoming Phases
- **Phase 2**: Enhanced Team Management
- **Phase 3**: Advanced Space Features (S3/Azure storage)
- **Phase 4**: Vision-to-Team Chatflow
- **Phase 5**: Advanced Collaboration
- **Phase 6**: Agentic Workflows

## 🔧 Development

### Backend Development
- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: Supabase JWT

### Frontend Development
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context
- **API Client**: Fetch API

## 📚 Documentation

See the `docs/` directory for detailed guides:
- `NUIFLO_WORKFORCE_ROADMAP.md` - Complete development roadmap
- `PHASE_1_STATUS.md` - Current implementation status
- `VPS_DEPLOYMENT_GUIDE.md` - Deployment instructions

## 🐳 Deployment

### VPS Deployment
```bash
./deploy-vps.sh
```

### Docker Deployment
```bash
docker-compose up -d
```

## 🔐 Security

- Row Level Security (RLS) policies
- JWT authentication via Supabase
- Input validation and sanitization
- Rate limiting and CORS protection

## 📊 Status

**Phase 1 Progress: 85% Complete**
- ✅ Backend Space Foundation: 100%
- ✅ Space-Aware Models: 100%
- ✅ API Endpoints: 100%
- ✅ Frontend Components: 70%
- ❌ Database Migration: 80%
- ❌ Integration Testing: 0%

---

**Built with ❤️ using CrewAI, FastAPI, and React** 