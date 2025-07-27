"""Health endpoints."""
from fastapi import APIRouter
from datetime import datetime
from sqlalchemy import text

router = APIRouter()

@router.get("/ping")
async def ping():
    """Basic ping endpoint."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

@router.get("/status")
async def health_status():
    """Comprehensive health check."""
    status = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "disconnected"
    }
    
    # Check database status - import here to avoid circular imports
    from ...core.database import engine
    
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            status["database"] = "connected"
        except Exception as e:
            status["database"] = f"error: {str(e)}"
    
    return status 