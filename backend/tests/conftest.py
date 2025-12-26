"""
Test configuration for FlagPilot - LangGraph Edition
"""

import pytest
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Configure environment before tests"""
    from config import settings
    
    # Configure LangSmith if available
    settings.configure_langsmith()
    
    yield


@pytest.fixture
def test_user_id():
    """Generate a unique test user ID"""
    import time
    return f"test_user_{int(time.time())}"
