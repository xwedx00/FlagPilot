"""
Auth Module (Secure)
====================
Provides JWT-based authentication using HS256 signatures.
Replaces insecure Header-based stub.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from config import settings

# Schema
class UserData(BaseModel):
    """User data from JWT"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: str = "user"

# Security Scheme
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserData:
    """
    Verify JWT token from Authorization header.
    
    Args:
        credentials: Bearer token from header
        
    Returns:
        UserData if valid
        
    Raises:
        HTTPException(401) if invalid
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Helper to handle "sub" vs "id"
        user_id = payload.get("sub") or payload.get("id")
        if not user_id:
            raise ValueError("Token missing 'sub' or 'id' claim")
            
        return UserData(
            id=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
            role=payload.get("role", "user")
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Alias for dependency injection
get_current_user = verify_token

# Helper for Tests: Generate Token
def create_test_token(user_id: str, email: str = "test@flagpilot.io") -> str:
    """Generate a valid token for testing"""
    payload = {
        "sub": user_id,
        "email": email,
        "name": "Test User",
        "role": "user"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
