"""Health endpoints."""
from fastapi import APIRouter
from datetime import datetime
from sqlalchemy import text
import httpx
import structlog

logger = structlog.get_logger()
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

@router.get("/ollama-test")
async def test_ollama():
    """Test Ollama connectivity and model response."""
    from ...core.config import get_settings
    
    settings = get_settings()
    ollama_url = f"{settings.ollama_host}/api/generate"
    
    test_prompt = {
        "model": settings.ollama_model,
        "prompt": "Write a simple 'Hello World' in Python",
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ollama_url, json=test_prompt)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "ollama_url": ollama_url,
                    "model": settings.ollama_model,
                    "response": result.get("response", ""),
                    "response_time": result.get("total_duration", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "ollama_url": ollama_url,
                    "model": settings.ollama_model,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Ollama test failed: {e}")
        return {
            "status": "error",
            "ollama_url": ollama_url,
            "model": settings.ollama_model,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/crewai-test")
async def test_crewai():
    """Test CrewAI integration with Ollama."""
    try:
        from crewai import Agent, Task, Crew, Process
        from ...core.config import get_settings
        
        settings = get_settings()
        
        # Create a simple test agent
        test_agent = Agent(
            role="Test Developer",
            goal="Write a simple Python function",
            backstory="You are a helpful Python developer",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "config_list": [{
                    "model": settings.ollama_model,
                    "api_base": settings.ollama_host,
                    "api_type": "open_ai",
                    "api_key": "ollama"
                }]
            }
        )
        
        # Create a simple task
        test_task = Task(
            description="Write a function that adds two numbers",
            agent=test_agent,
            expected_output="A Python function that adds two numbers"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "status": "success",
            "crewai_version": "0.150.0",
            "ollama_model": settings.ollama_model,
            "ollama_host": settings.ollama_host,
            "result": result.raw,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"CrewAI test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 