#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : conftest.py
@Desc    : Centralized fixtures for FlagPilot Backend Tests (LIVE Mode)

IMPORTANT: These tests use LIVE LLM (OpenRouter) and LIVE RAGFlow.
No mocking - all responses are real API calls.

Requirements:
- OPENROUTER_API_KEY environment variable
- Running RAGFlow instance (optional for some tests)
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import pytest

# Ensure backend modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test data paths
TEST_DATA_PATH = Path(__file__).parent / "data"


# =============================================================================
# Session Configuration
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def init_config():
    """
    Initialize test configuration.
    
    LIVE MODE: Uses real API keys from environment.
    """
    # Verify required API keys are present
    if not os.environ.get("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set - required for live tests")
    
    # Set up logging
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Configure MetaGPT environment
    from config import settings
    settings.configure_metagpt_env()
    
    yield
    
    # Cleanup after all tests
    print("\n[Test Session Complete]")


# =============================================================================
# Live LLM Fixture (No Mocking)
# =============================================================================

@pytest.fixture(scope="session")
def live_llm():
    """
    Get the live LLM configured from OpenRouter.
    
    Uses MetaGPT's LLM which is configured via environment variables.
    All responses are real API calls - NO MOCKING.
    """
    from metagpt.llm import LLM
    
    try:
        llm = LLM()
        return llm
    except Exception as e:
        pytest.skip(f"LLM not configured properly: {e}")


# =============================================================================
# Live RAGFlow Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def ragflow_client():
    """
    Get live RAGFlow client.
    
    NO MOCKING - all operations are real.
    """
    from ragflow.client import get_ragflow_client, RAGFlowClient
    from config import settings
    
    try:
        client = get_ragflow_client()
        return client
    except Exception as e:
        # Create a mock-like client for tests if RAGFlow not available
        pytest.skip(f"RAGFlow not available: {e}")


@pytest.fixture(scope="session")
def seeded_ragflow(ragflow_client):
    """
    RAGFlow client with seed documents (if available).
    
    Seeds test documents for testing search functionality.
    """
    test_user_id = "pytest_live_user"
    
    # Seed documents for testing
    seed_docs = [
        {
            "filename": "sample_contract.txt",
            "content": """
FREELANCE SERVICE AGREEMENT

This Agreement is entered into between:
Client: ABC Corporation ("Client")
Freelancer: Test User ("Contractor")

1. SERVICES
The Contractor agrees to provide web development services.

2. PAYMENT TERMS
- Total Project Fee: $5,000 USD
- Payment Schedule: 50% upfront, 50% upon completion
- Payment Due: Net 30 days from invoice date
- Late Payment Fee: 1.5% per month

3. TIMELINE
- Project Start: January 1, 2024
- Final Delivery: March 1, 2024

4. INTELLECTUAL PROPERTY
All work product owned by Client upon full payment.
"""
        },
        {
            "filename": "job_posting_examples.txt",
            "content": """
JOB POSTING ANALYSIS - EXAMPLES

LEGITIMATE JOB POSTING:
- Clear company name and website
- Specific technical requirements
- Reasonable budget range ($50-100/hr)
- Defined project scope
- Professional communication

RED FLAGS TO WATCH FOR:
- Vague job descriptions
- Unusually high pay for simple tasks
- Requests for upfront payment from freelancer
- Personal information requests before hiring
- Pressure to move off-platform
"""
        }
    ]
    
    print(f"\n[Seeding RAGFlow] Test user: {test_user_id}")
    
    yield {
        "client": ragflow_client,
        "test_user_id": test_user_id,
        "seed_docs": seed_docs
    }


# =============================================================================
# Agent Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def agent_registry():
    """Get the agent registry with all registered agents"""
    from agents.registry import registry
    return registry


@pytest.fixture
def contract_guardian(agent_registry):
    """Get ContractGuardian agent instance"""
    agent_class = agent_registry.get_agent_class("contract_guardian")
    if not agent_class:
        pytest.skip("ContractGuardian not available")
    return agent_class()


@pytest.fixture
def job_authenticator(agent_registry):
    """Get JobAuthenticator agent instance"""
    agent_class = agent_registry.get_agent_class("job_authenticator")
    if not agent_class:
        pytest.skip("JobAuthenticator not available")
    return agent_class()


# =============================================================================
# Context Fixtures
# =============================================================================

@pytest.fixture
def test_user_id():
    """Standard test user ID"""
    return "pytest_live_user"


@pytest.fixture
def metagpt_context():
    """Fresh MetaGPT Context for each test"""
    from metagpt.context import Context
    return Context()


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live API calls"
    )
