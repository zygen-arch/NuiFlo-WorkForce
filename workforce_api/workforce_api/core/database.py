"""Database utilities (SQLAlchemy with Supabase).
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global variables for engine and session
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection."""
    global engine, SessionLocal
    
    try:
        # Create synchronous engine for Supabase
        engine = create_engine(
            settings.supabase_db_url,
            echo=settings.debug,
            # Use connection pooling but allow graceful degradation
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("✅ Database connected successfully")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Database connection failed: {e}")
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