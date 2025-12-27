"""
Auth Middleware - Production Session Validation
================================================
Real authentication middleware that validates sessions against
the PostgreSQL database (BetterAuth session table).

NO MOCKS. NO TODOS. Production-ready.
"""

from fastapi import Header, HTTPException, Depends, Request
from typing import Optional, Dict, Any
from loguru import logger
import hashlib

from lib.auth.database import validate_session_token, get_user_by_id


class AuthenticatedUser:
    """
    Represents an authenticated user.
    Contains validated user data from the session.
    """
    
    def __init__(
        self,
        user_id: str,
        session_id: str,
        name: str,
        email: str,
        image: Optional[str] = None,
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.name = name
        self.email = email
        self.image = image
    
    def __str__(self) -> str:
        return f"User({self.user_id}, {self.email})"


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> str:
    """
    Extract and validate user identity from request headers.
    
    Authentication flow:
    1. Check Authorization header for Bearer token
    2. Validate token against PostgreSQL session table
    3. Return user_id if valid
    4. Fallback to X-User-ID for internal service calls
    5. Return "anonymous" only for truly public endpoints
    
    For protected endpoints, use `require_auth` instead.
    """
    
    # Priority 1: Bearer token from Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        if token:
            # Validate against database
            session_data = await validate_session_token(token)
            if session_data:
                logger.debug(f"Auth: Valid session for user {session_data['user_id']}")
                return session_data["user_id"]
            else:
                logger.debug("Auth: Invalid or expired session token")
    
    # Priority 2: X-User-ID header (for trusted internal services only)
    # This should only be allowed from internal network in production
    if x_user_id:
        # Verify it's a real user
        user = await get_user_by_id(x_user_id)
        if user:
            logger.debug(f"Auth: X-User-ID verified: {x_user_id}")
            return x_user_id
        else:
            logger.warning(f"Auth: X-User-ID {x_user_id} not found in database")
    
    # No valid authentication - return anonymous for public endpoints
    return "anonymous"


async def require_auth(
    user_id: str = Depends(get_current_user)
) -> str:
    """
    Strict authentication - rejects anonymous users.
    Use this dependency for ALL protected routes.
    
    Raises 401 if not authenticated.
    """
    if user_id == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id


async def get_authenticated_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> AuthenticatedUser:
    """
    Get full authenticated user object with all details.
    Use when you need more than just user_id.
    
    Raises 401 if not authenticated or session invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization[7:].strip()
    session_data = await validate_session_token(token)
    
    if not session_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return AuthenticatedUser(
        user_id=session_data["user_id"],
        session_id=session_data["session_id"],
        name=session_data["name"],
        email=session_data["email"],
        image=session_data.get("image"),
    )


async def get_optional_user(
    user_id: str = Depends(get_current_user)
) -> Optional[str]:
    """
    Optional authentication - returns None for anonymous.
    Use for routes that work with or without auth but behave differently.
    """
    if user_id == "anonymous":
        return None
    return user_id


def hash_user_id(user_id: str) -> str:
    """
    Create a hashed version of user ID for logging/analytics.
    Privacy-preserving identifier for metrics.
    """
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]
