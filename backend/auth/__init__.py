"""
Auth Module (Hybrid: Better Auth + JWT)
=======================================
Supports:
1. Better Auth: Verifies session tokens against the `session` table.
2. JWT: Fallback for testing/legacy scripts (using HS256).
"""

from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import jwt

from config import settings
from models import get_db, Session, User

# Schema
class UserData(BaseModel):
    """User data from Auth Source"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: str = "user"

from fastapi import Request

# Security Scheme (Optional so we can check cookies manually)
security = HTTPBearer(auto_error=False)

async def verify_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserData:
    """
    Verify Token (Hybrid Strategy)
    1. Check Authorization Header (Bearer)
    2. Check Cookie (better-auth.session_token)
    3. Check DB for Better Auth Session
    """
    token = None
    
    # Try Header
    if credentials:
        token = credentials.credentials
    # Try Cookie
    elif request.cookies.get("better-auth.session_token"):
        token = request.cookies.get("better-auth.session_token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # --- Strategy 1: Better Auth Session (DB) ---
    try:
        query = select(Session).where(Session.token == token)
        result = await db.execute(query)
        session_record = result.scalars().first()
        
        if session_record:
            # Check Expiry
            if session_record.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired"
                )
            
            return UserData(id=session_record.user_id, role="user")
            
    except Exception as e:
        # Log error in production
        pass

    # If we get here, session validation failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Alias for dependency injection
get_current_user = verify_token

# Helper for Tests: Generate Token
def create_test_token(user_id: str, email: str = "test@flagpilot.io") -> str:
    """Generate a valid JWT for testing"""
    payload = {
        "sub": user_id,
        "email": email,
        "name": "Test User",
        "role": "user",
        "exp": 9999999999 # Far future
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
