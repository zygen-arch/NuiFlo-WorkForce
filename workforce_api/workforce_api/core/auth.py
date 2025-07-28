"""Authentication utilities for Supabase integration."""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import requests
from typing import Optional
import logging

from .config import get_settings
from .database import get_db_dependency

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()

class SupabaseAuth:
    """Supabase authentication handler."""
    
    def __init__(self):
        self.supabase_url = getattr(settings, 'supabase_url', None)
        self.supabase_anon_key = getattr(settings, 'supabase_anon_key', None)
        
        if not self.supabase_url or not self.supabase_anon_key:
            logger.warning("Supabase credentials not configured. Authentication disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify Supabase JWT token and return user info."""
        if not self.enabled:
            # For development: return dummy user if Supabase not configured
            logger.warning("Authentication disabled - using dummy user")
            return {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@nuiflo.com"}
        
        try:
            # Verify token with Supabase
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": self.supabase_anon_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                logger.error(f"Token verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

# Global auth instance
auth_handler = SupabaseAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and verify user from Supabase JWT token.
    Returns the user ID (UUID string).
    """
    try:
        token = credentials.credentials
        
        # Verify token
        user_data = auth_handler.verify_token(token)
        
        if not user_data or "id" not in user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = user_data["id"]
        logger.debug(f"Authenticated user: {user_id}")
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Optional authentication - returns user ID if authenticated, None otherwise.
    Useful for endpoints that can work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def require_auth(func):
    """
    Decorator to require authentication for endpoint functions.
    Usage:
    
    @require_auth
    def my_endpoint(current_user_id: str = Depends(get_current_user)):
        pass
    """
    return func

# Utility functions for common auth checks
def check_user_owns_team(user_id: str, team_id: int, db: Session) -> bool:
    """Check if user owns a specific team."""
    try:
        from ..models.team import Team
        
        team = db.query(Team).filter(
            Team.id == team_id,
            Team.auth_owner_id == user_id
        ).first()
        
        return team is not None
    except Exception as e:
        logger.error(f"Error checking team ownership: {e}")
        return False

def ensure_team_access(user_id: str, team_id: int, db: Session):
    """Ensure user has access to team, raise 403 if not."""
    if not check_user_owns_team(user_id, team_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't own this team"
        ) 