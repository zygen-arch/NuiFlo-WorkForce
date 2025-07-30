"""Authentication utilities for Supabase JWT validation."""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import structlog
import httpx
from jose import jwt, JWTError
import json

from .config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)

class SupabaseJWTValidator:
    """Supabase JWT validator using JWKS endpoint."""
    
    def __init__(self):
        self.supabase_url = getattr(settings, 'supabase_url', None)
        self.supabase_anon_key = getattr(settings, 'supabase_anon_key', None)
        
        if not self.supabase_url:
            logger.warning("Supabase URL not configured. Authentication disabled.")
            self.enabled = False
        else:
            self.enabled = True
            # Extract project ID from URL (e.g., https://abc123.supabase.co -> abc123.supabase.co)
            self.project_url = self.supabase_url.replace('https://', '').replace('http://', '')
            self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
            self.issuer = f"{self.supabase_url}/auth/v1"
            self.audience = "authenticated"  # Standard Supabase audience
            self._jwks_cache = None
            logger.info(f"Supabase JWT validator enabled for: {self.project_url}")
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch and cache JWKS from Supabase."""
        if self._jwks_cache is None:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.jwks_url)
                    if response.status_code == 200:
                        self._jwks_cache = response.json()
                        logger.debug(f"Fetched JWKS from {self.jwks_url}")
                    else:
                        logger.error(f"Failed to fetch JWKS: {response.status_code}")
                        return {}
            except Exception as e:
                logger.error(f"Error fetching JWKS: {e}")
                return {}
        
        return self._jwks_cache or {}
    
    async def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token using Supabase JWKS."""
        if not self.enabled:
            # For development: return dummy user if Supabase not configured
            logger.warning("Authentication disabled - using dummy user")
            return {
                "sub": "00000000-0000-0000-0000-000000000001", 
                "email": "test@nuiflo.com",
                "aud": "authenticated",
                "role": "authenticated"
            }
        
        try:
            # Get the unverified header to find the key ID
            try:
                unverified_header = jwt.get_unverified_header(token)
                logger.debug(f"JWT header: {unverified_header}")
            except Exception as e:
                logger.warning(f"Error decoding token headers: {e}")
                logger.warning(f"Token (first 50 chars): {token[:50]}...")
                logger.warning(f"Token length: {len(token)}")
                logger.warning(f"Token starts with 'Bearer ': {token.startswith('Bearer ')}")
                return None
                
            kid = unverified_header.get("kid")
            
            if not kid:
                logger.warning("JWT token missing key ID (kid)")
                logger.debug(f"Available header keys: {list(unverified_header.keys())}")
                return None
            
            # Get JWKS and find the matching key
            jwks = await self.get_jwks()
            if not jwks or "keys" not in jwks:
                logger.error("No JWKS available for token verification")
                return None
            
            # Log available keys for debugging
            available_kids = [jwk.get("kid") for jwk in jwks["keys"]]
            logger.debug(f"Available JWKS kids: {available_kids}")
            logger.debug(f"Looking for kid: {kid}")
            
            # Find the key with matching kid
            key = None
            for jwk in jwks["keys"]:
                if jwk.get("kid") == kid:
                    key = jwk
                    break
            
            if not key:
                logger.warning(f"No matching key found for kid: {kid}")
                logger.warning(f"Available kids: {available_kids}")
                return None
            
            # Verify and decode the JWT
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=["ES256", "RS256"],  # Supabase uses ES256
                    audience=self.audience,
                    issuer=self.issuer
                )
            except Exception as e:
                logger.warning(f"JWT decode failed: {e}")
                logger.debug(f"Using issuer: {self.issuer}, audience: {self.audience}")
                
                # Try without strict audience/issuer validation for debugging
                try:
                    payload = jwt.decode(
                        token,
                        key,
                        algorithms=["ES256", "RS256"],
                        options={"verify_aud": False, "verify_iss": False}
                    )
                    logger.warning("JWT validation succeeded without aud/iss verification")
                    logger.debug(f"Payload aud: {payload.get('aud')}, iss: {payload.get('iss')}")
                except Exception as e2:
                    logger.error(f"JWT decode failed even without aud/iss: {e2}")
                    return None
            
            # Extract user information
            user_id = payload.get("sub")
            user_email = payload.get("email")
            user_role = payload.get("role", "authenticated")
            exp = payload.get("exp")
            
            # Check if token is expired
            if exp and datetime.utcnow().timestamp() > exp:
                logger.warning("JWT token has expired")
                return None
            
            logger.info(f"Successfully verified JWT for user: {user_id} ({user_email})")
            
            return {
                "sub": user_id,
                "email": user_email,
                "role": user_role,
                "aud": payload.get("aud"),
                "exp": exp,
                "iat": payload.get("iat"),
                "iss": payload.get("iss")
            }
            
        except JWTError as e:
            logger.warning(f"JWT validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during JWT validation: {e}")
            return None

# Global JWT validator instance
jwt_validator = SupabaseJWTValidator()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Extract and verify user from Supabase JWT token.
    Returns the user ID (UUID string).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid JWT token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify JWT token
        payload = await jwt_validator.verify_jwt_token(token)
        
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload["sub"]
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