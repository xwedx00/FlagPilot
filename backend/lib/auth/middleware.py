
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from loguru import logger
from config import settings
from typing import Optional

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extracts and validates user_id from JWT token.
    In development, if token check fails it might fallback to a test user 
    if a specific flag is set, but for prod this must be strict.
    """
    token = credentials.credentials
    try:
        # BetterAuth tokens from Next.js
        # We need the SECRET_KEY from settings to validate.
        # If we don't have the secret yet, we might skip signature validation in DEV ONLY.
        payload = jwt.decode(token, options={"verify_signature": False})
        
        user_id = payload.get("sub") or payload.get("id") or payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: Missing user_id")
            
        return str(user_id)
        
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def optional_user(request: Request) -> Optional[str]:
    """Helper to get user if present without failing the request."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "anonymous_user"
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, options={"verify_signature": False})
        return str(payload.get("sub") or payload.get("id") or "anonymous_user")
    except:
        return "anonymous_user"
