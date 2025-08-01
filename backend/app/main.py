"""Entry point FastAPI app."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import logging
import time
from collections import defaultdict, deque
from typing import Dict, Deque

from .core.config import get_settings
from .core.database import init_database
from .api.v1 import health_router, teams_router, spaces_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, Deque[float]] = defaultdict(deque)

class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.window_seconds = 60
        self.settings = get_settings()  # Add settings access
    
    async def __call__(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        user_calls = rate_limit_storage[client_ip]
        while user_calls and user_calls[0] < current_time - self.window_seconds:
            user_calls.popleft()
        
        # Check rate limit
        if len(user_calls) >= self.calls_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record this call
        user_calls.append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # More permissive CSP to support FastAPI docs and Swagger UI
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https:; "
            "font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com data:; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:"
        )
        
        return response

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
    * **Team Spaces**: Virtual boundaries for agent operations and storage
    
    ## Authentication
    
    Currently using dummy authentication (user_id=1). Production authentication will be implemented.
    
    ## Usage for Frontend Integration
    
    1. **Create Team**: `POST /api/v1/teams/` with team details and roles
    2. **List Teams**: `GET /api/v1/teams/` to get all user teams
    3. **Get Status**: `GET /api/v1/teams/{id}/status` for detailed metrics
    4. **Execute Team**: `POST /api/v1/teams/{id}/execute` to run AI workflows
    5. **Space Management**: `GET /api/v1/spaces/` to manage team spaces
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

# Add rate limiting and security headers (disabled for development)
rate_limiter = RateLimitMiddleware(calls_per_minute=10000)  # Very high limit for development testing
app.middleware("http")(rate_limiter)

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
app.include_router(spaces_router, prefix="/api/v1/spaces", tags=["spaces"])

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