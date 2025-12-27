"""
Auth Middleware - JWT/Session Validation for FastAPI
=====================================================
Provides authentication utilities for protected routes.
"""

from fastapi import Header, HTTPException, Depends, Request
from typing import Optional
from loguru import logger
import hashlib


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> str:
    """
    Extract and validate user identity from request headers.
    
    Supports multiple auth patterns:
    1. Authorization: Bearer <token> - JWT/session token
    2. X-User-ID header - Direct user ID (for internal/trusted calls)
    3. Anonymous fallback - Returns "anonymous" for public routes
    
    In production, this should validate against your auth provider:
    - BetterAuth session validation
    - JWT signature verification
    - Session lookup in database
    """
    
    # Priority 1: Authorization header (Bearer token)
    if authorization:
        try:
            if authorization.startswith("Bearer "):
                token = authorization[7:]
                # For BetterAuth, the token might be the user ID directly
                # or a session token that needs lookup
                if token and len(token) > 0:
                    # Basic validation - in production, verify against session store
                    logger.debug(f"Auth: Token received (length: {len(token)})")
                    return token
            else:
                # Legacy: treat whole header as user ID
                return authorization
        except Exception as e:
            logger.warning(f"Auth token parse error: {e}")
    
    # Priority 2: X-User-ID header (for internal services)
    if x_user_id:
        logger.debug(f"Auth: X-User-ID header: {x_user_id}")
        return x_user_id
    
    # Priority 3: Anonymous (for public routes that accept it)
    logger.debug("Auth: No credentials provided, returning anonymous")
    return "anonymous"


async def require_auth(
    user_id: str = Depends(get_current_user)
) -> str:
    """
    Strict authentication - rejects anonymous users.
    Use this dependency for protected routes.
    """
    if user_id == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id


async def get_optional_user(
    user_id: str = Depends(get_current_user)
) -> Optional[str]:
    """
    Optional authentication - returns None for anonymous.
    Use this for routes that work with or without auth.
    """
    if user_id == "anonymous":
        return None
    return user_id


class RoleChecker:
    """
    Role-based access control dependency.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker(["admin", "enterprise"]))])
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        user_id: str = Depends(require_auth),
        # In production, add: user_service: UserService = Depends(get_user_service)
    ) -> str:
        # TODO: Lookup user role from database
        # For now, allow all authenticated users
        # user = await user_service.get_user(user_id)
        # if user.role not in self.allowed_roles:
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")
        logger.debug(f"RoleChecker: User {user_id} accessing role-protected route")
        return user_id


def hash_user_id(user_id: str) -> str:
    """
    Create a hashed version of user ID for logging/analytics.
    Useful for privacy-preserving metrics.
    """
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]
