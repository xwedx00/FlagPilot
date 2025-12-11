"""
Test Configuration
==================
Centralized configuration for test credentials and helpers.

Usage:
    Set environment variables or update defaults after GitHub authentication.
    
Environment Variables:
    TEST_USER_ID: The user ID from the database
    TEST_SESSION_TOKEN: The session token from browser cookies
"""

import os
import asyncio
from typing import Optional, Tuple

# Configuration - Update these after GitHub authentication
# Or set via environment variables
TEST_USER_ID = os.environ.get("TEST_USER_ID", "T0Ak6rbl4YBi7nvoBphQuVyOxbv3wwew")
TEST_SESSION_TOKEN = os.environ.get("TEST_SESSION_TOKEN", "rGrnTidO69mBdvcB8vkjr33l57N1g5xX")

# API Configuration
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
OUTPUT_DIR = os.path.dirname(__file__) + "/../"


def get_auth_headers() -> dict:
    """Get authentication headers for API requests"""
    if not TEST_SESSION_TOKEN:
        raise ValueError(
            "TEST_SESSION_TOKEN not set. Either:\n"
            "1. Set TEST_SESSION_TOKEN env var, or\n"
            "2. Update TEST_SESSION_TOKEN in test_config.py after GitHub login"
        )
    return {"Authorization": f"Bearer {TEST_SESSION_TOKEN}"}


def get_user_id() -> str:
    """Get the test user ID"""
    if not TEST_USER_ID:
        raise ValueError(
            "TEST_USER_ID not set. Either:\n"
            "1. Set TEST_USER_ID env var, or\n"
            "2. Update TEST_USER_ID in test_config.py after GitHub login"
        )
    return TEST_USER_ID


async def lookup_session_from_db() -> Tuple[Optional[str], Optional[str]]:
    """
    Look up a valid session from the database.
    Returns (user_id, session_token) tuple.
    
    Useful for auto-populating test credentials.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from sqlalchemy import select, text
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        
        db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://flagpilot:flagpilot@localhost:5432/flagpilot")
        # Convert to async URL if needed
        if "postgresql://" in db_url and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Find a non-expired session
            result = await session.execute(
                text("""
                    SELECT s.user_id, s.token 
                    FROM session s 
                    WHERE s.expires_at > NOW() 
                    ORDER BY s.created_at DESC 
                    LIMIT 1
                """)
            )
            row = result.fetchone()
            
            if row:
                return row[0], row[1]
            
        return None, None
        
    except Exception as e:
        print(f"[test_config] DB lookup failed: {e}")
        return None, None


def log_and_print(message: str, output_file: str):
    """Log message to console and file"""
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# NOTE: Auto-lookup is disabled to prevent picking up expired/invalid sessions
# The hardcoded TEST_USER_ID and TEST_SESSION_TOKEN above are the source of truth
# If you need to update credentials, manually edit the values above after GitHub login

# Auto-populate is DISABLED - use the hardcoded values above
# if not TEST_USER_ID or not TEST_SESSION_TOKEN:
#     try:
#         loop = asyncio.new_event_loop()
#         _user_id, _token = loop.run_until_complete(lookup_session_from_db())
#         loop.close()
#         
#         if _user_id and _token:
#             TEST_USER_ID = TEST_USER_ID or _user_id
#             TEST_SESSION_TOKEN = TEST_SESSION_TOKEN or _token
#             print(f"[test_config] Auto-populated from DB: user_id={_user_id[:8]}...")
#     except Exception as e:
#         # Silently fail - user can manually configure
#         pass

