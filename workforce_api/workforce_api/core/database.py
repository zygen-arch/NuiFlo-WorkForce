"""Database utilities (SQLAlchemy with Supabase).
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging
import structlog

from .config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global variables for engine and session
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection."""
    global engine, SessionLocal
    
    try:
        # Get database URL
        db_url = settings.supabase_db_url
        logger.info(f"Attempting database connection to: {db_url.split('@')[0]}@***")
        
        # Create synchronous engine for Supabase
        engine = create_engine(
            db_url,
            echo=settings.debug,
            # Use connection pooling but allow graceful degradation
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=30,
            pool_size=5,
            max_overflow=10,
        )
        
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        
        # Test connection with more detailed error reporting
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, version() as postgres_version"))
            row = result.fetchone()
            logger.info(f"✅ Database connected successfully - Test query result: {row[0]}")
            logger.info(f"PostgreSQL version: {row[1]}")
        
        logger.info("✅ Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        logger.error(f"Database URL format: {db_url.split('@')[0] if '@' in db_url else 'Invalid URL format'}@***")
        
        # More specific error messages
        if "Name or service not known" in str(e):
            logger.error("DNS resolution failed - check if the database host is reachable")
        elif "password authentication failed" in str(e):
            logger.error("Authentication failed - check username and password")
        elif "SSL connection has been closed unexpectedly" in str(e):
            logger.error("SSL connection issue - check SSL mode and certificates")
        elif "Connection refused" in str(e):
            logger.error("Connection refused - check if database server is running and port is correct")
        else:
            logger.error(f"Unexpected database error: {type(e).__name__}")
        
        logger.warning("🔄 Application will start without database (some features disabled)")
        return False


@contextmanager
def get_db() -> Session:
    """Dependency for FastAPI - provides database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Please check your connection.")
    
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db_dependency():
    """FastAPI dependency wrapper that handles missing database gracefully."""
    try:
        with get_db() as session:
            yield session
    except RuntimeError as e:
        logger.error(f"Database dependency failed: {e}")
        # You could yield None here and handle it in your endpoints
        raise 