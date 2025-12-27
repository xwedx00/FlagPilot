"""
Auth Module
===========
Authentication utilities for FlagPilot backend.
"""

from lib.auth.middleware import (
    get_current_user,
    require_auth,
    get_optional_user,
    RoleChecker,
    hash_user_id,
)

__all__ = [
    "get_current_user",
    "require_auth", 
    "get_optional_user",
    "RoleChecker",
    "hash_user_id",
]
