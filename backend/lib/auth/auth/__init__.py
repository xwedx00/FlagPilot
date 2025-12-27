"""
Auth Module
===========
Production authentication for FlagPilot backend.
Validates sessions against the PostgreSQL database (BetterAuth tables).
"""

from lib.auth.middleware import (
    get_current_user,
    require_auth,
    get_optional_user,
    get_authenticated_user,
    AuthenticatedUser,
    hash_user_id,
)
from lib.auth.database import (
    DatabasePool,
    validate_session_token,
    get_user_by_id,
)

__all__ = [
    # Middleware dependencies
    "get_current_user",
    "require_auth", 
    "get_optional_user",
    "get_authenticated_user",
    "AuthenticatedUser",
    "hash_user_id",
    # Database utilities
    "DatabasePool",
    "validate_session_token",
    "get_user_by_id",
]
