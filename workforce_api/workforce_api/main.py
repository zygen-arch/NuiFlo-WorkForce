"""Entry point FastAPI app."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.config import get_settings
from .core.database import init_database
from .api.v1 import health_router, teams_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="NuiFlo WorkForce API",
    version="0.1.0",
    description="""
    # NuiFlo WorkForce API
    
    AI Team Management Platform powered by CrewAI. Build, deploy, and scale virtual teams of AI agents for custom workflows.
    
    ## Features
    
    * **Team Management**: Create and manage AI teams with custom roles
    * **Role Configuration**: Define agent expertise levels and LLM models  
    * **Budget Tracking**: Monitor spending and set monthly budgets
    * **Real-time Execution**: Execute teams using CrewAI framework
    * **Status Monitoring**: Track team performance and utilization
    
    ## Authentication
    
    Currently using dummy authentication (user_id=1). Production authentication will be implemented.
    
    ## Usage for Frontend Integration
    
    1. **Create Team**: `POST /api/v1/teams/` with team details and roles
    2. **List Teams**: `GET /api/v1/teams/` to get all user teams
    3. **Get Status**: `GET /api/v1/teams/{id}/status` for detailed metrics
    4. **Execute Team**: `POST /api/v1/teams/{id}/execute` to run AI workflows
    
    ## Contact
    
    * **Developer**: NuiFlo Team
    * **Email**: team@nuiflo.com
    * **Repository**: [GitHub](https://github.com/nuiflo/workforce)
    """,
    contact={
        "name": "NuiFlo Team",
        "email": "team@nuiflo.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://nuiflo-workforce.onrender.com",
            "description": "Production server"
        }
    ],
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints for monitoring service status"
        },
        {
            "name": "teams",
            "description": "Team management operations - the core of the AI workforce platform"
        }
    ]
)

# CORS configuration - allow all origins for development since Lovable uses dynamic URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting NuiFlo WorkForce API...")
    
    # Initialize database
    db_connected = init_database()
    if db_connected:
        logger.info("✅ All services initialized successfully")
    else:
        logger.warning("⚠️  Started with limited functionality (database unavailable)")

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(teams_router, prefix="/api/v1/teams", tags=["teams"])

@app.get("/", tags=["root"])
async def root():
    """
    Welcome endpoint with API information.
    
    Returns basic information about the NuiFlo WorkForce API.
    """
    return {
        "message": "Welcome to NuiFlo WorkForce API",
        "version": "0.1.0",
        "description": "AI Team Management Platform powered by CrewAI",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
        "status": "operational"
    } 