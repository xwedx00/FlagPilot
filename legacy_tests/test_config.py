"""
Test Configuration
==================
Centralized configuration for test credentials and helpers.

Usage:
    Set environment variables or update defaults after GitHub authentication.
    
Environment Variables:
    TEST_USER_ID: The user ID for testing
    TEST_SESSION_TOKEN: The session token from browser cookies
"""

import os
from typing import Optional, Tuple

# Configuration - Update these for testing
# Or set via environment variables
TEST_USER_ID = os.environ.get("TEST_USER_ID", "test-user-id")
TEST_SESSION_TOKEN = os.environ.get("TEST_SESSION_TOKEN", "test-session-token")

# API Configuration
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
OUTPUT_DIR = os.path.dirname(__file__) + "/../"


def get_auth_headers() -> dict:
    """Get authentication headers for API requests"""
    if not TEST_SESSION_TOKEN:
        raise ValueError(
            "TEST_SESSION_TOKEN not set. Either:\n"
            "1. Set TEST_SESSION_TOKEN env var, or\n"
            "2. Update TEST_SESSION_TOKEN in test_config.py"
        )
    return {"Authorization": f"Bearer {TEST_SESSION_TOKEN}"}


def get_user_id() -> str:
    """Get the test user ID"""
    if not TEST_USER_ID:
        raise ValueError(
            "TEST_USER_ID not set. Either:\n"
            "1. Set TEST_USER_ID env var, or\n"
            "2. Update TEST_USER_ID in test_config.py"
        )
    return TEST_USER_ID


def log_and_print(message: str, output_file: str):
    """Log message to console and file"""
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# NOTE: Database lookup removed - backend is now database-free
# Test credentials must be configured manually via environment variables
