#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : conftest.py
@Desc    : Centralized fixtures for FlagPilot Backend Tests (LIVE Mode)

IMPORTANT: These tests use LIVE LLM (OpenRouter) and LIVE RAGFlow.
No mocking - all responses are real API calls.

Requirements:
- OPENROUTER_API_KEY environment variable
- RAGFLOW_API_KEY environment variable
- Running RAGFlow instance
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

import pytest

# Ensure backend modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test data paths
TEST_DATA_PATH = Path(__file__).parent / "data"
SEED_DOCUMENTS_PATH = TEST_DATA_PATH / "seed_documents"


# =============================================================================
# Session Configuration
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def init_config():
    """
    Initialize test configuration.
    
    LIVE MODE: No mocking - uses real API keys from environment.
    """
    # Verify required API keys are present
    if not os.environ.get("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set - required for live tests")
    
    if not os.environ.get("RAGFLOW_API_KEY"):
        pytest.skip("RAGFLOW_API_KEY not set - required for live tests")
    
    # Set up logging
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
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
    
    This uses the actual configured LLM from config.py.
    All responses are real API calls - NO MOCKING.
    """
    from config import get_configured_llm
    
    llm = get_configured_llm()
    
    # Verify LLM is properly configured
    if llm is None:
        pytest.skip("LLM not configured properly")
    
    return llm


# =============================================================================
# Live RAGFlow Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def ragflow_client():
    """
    Get live RAGFlow client.
    
    NO MOCKING - all operations are real.
    """
    from ragflow.client import RAGFlowClient
    
    client = RAGFlowClient()
    
    if not client.is_connected:
        pytest.skip("RAGFlow not available - cannot run live tests")
    
    return client


@pytest.fixture(scope="session")
def seeded_ragflow(ragflow_client):
    """
    RAGFlow client with seed documents uploaded.
    
    Seeds:
    1. Sample freelance contract
    2. Job posting examples
    3. Payment terms document
    
    These documents are uploaded before tests and cleaned up after.
    """
    test_user_id = "pytest_live_user"
    
    # Seed documents
    seed_docs = [
        {
            "filename": "sample_contract.txt",
            "content": """
FREELANCE SERVICE AGREEMENT

This Agreement is entered into as of [Date] between:
Client: ABC Corporation ("Client")
Freelancer: Test User ("Contractor")

1. SERVICES
The Contractor agrees to provide web development services including:
- Frontend development using React
- Backend API development
- Database design and implementation

2. PAYMENT TERMS
- Total Project Fee: $5,000 USD
- Payment Schedule: 50% upfront, 50% upon completion
- Payment Due: Net 30 days from invoice date
- Late Payment Fee: 1.5% per month

3. TIMELINE
- Project Start: January 1, 2024
- Milestone 1 (Frontend): February 1, 2024
- Final Delivery: March 1, 2024

4. INTELLECTUAL PROPERTY
All work product created shall be owned by the Client upon full payment.

5. TERMINATION
Either party may terminate with 14 days written notice.
Client responsible for payment of work completed.

6. LIMITATION OF LIABILITY
Contractor's liability limited to amount of fees paid.
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

SAMPLE LEGITIMATE POSTING:
"Looking for experienced React developer for 3-month project.
Must have: 3+ years React, TypeScript, REST APIs
Budget: $8,000-12,000
Timeline: March-May 2024
Company: TechStartup Inc (verified)"

SAMPLE SUSPICIOUS POSTING:
"Easy money! Just need to process payments. $500/day guaranteed.
No experience needed. Contact via personal email only."
"""
        },
        {
            "filename": "payment_best_practices.txt",
            "content": """
FREELANCER PAYMENT BEST PRACTICES

1. ESCROW PROTECTION
- Always use platform escrow when available
- Never accept direct wire transfers from new clients
- Milestone-based payments reduce risk

2. INVOICE GUIDELINES
- Include detailed work description
- Specify payment terms clearly
- Track all hours/deliverables

3. DISPUTE PREVENTION
- Get everything in writing
- Confirm scope changes with amendments
- Document all communications

4. LATE PAYMENT HANDLING
- Send reminder at Net+7 days
- Formal notice at Net+14 days
- Consider collections at Net+30 days

5. PLATFORM-SPECIFIC TIPS
- Upwork: Use hourly with screenshots for protection
- Fiverr: Wait for order completion before delivery
- Freelancer.com: Milestone payments recommended
"""
        }
    ]
    
    print(f"\n[Seeding RAGFlow] Uploading {len(seed_docs)} documents for user: {test_user_id}")
    
    # Upload seed documents
    async def seed_documents():
        for doc in seed_docs:
            try:
                await ragflow_client.add_user_document(
                    user_id=test_user_id,
                    content=doc["content"].encode("utf-8"),
                    filename=doc["filename"]
                )
                print(f"  ✓ Uploaded: {doc['filename']}")
            except Exception as e:
                print(f"  ✗ Failed to upload {doc['filename']}: {e}")
    
    # Run seeding
    asyncio.get_event_loop().run_until_complete(seed_documents())
    
    # Wait for parsing
    print("[Seeding RAGFlow] Waiting for document parsing...")
    time.sleep(5)  # Give RAGFlow time to parse
    
    yield {
        "client": ragflow_client,
        "test_user_id": test_user_id,
        "seed_docs": seed_docs
    }
    
    # Cleanup after tests
    print("\n[Cleanup] Removing test dataset...")
    try:
        dataset_name = ragflow_client.get_user_dataset_name(test_user_id)
        datasets = ragflow_client._client.list_datasets(name=dataset_name)
        if datasets:
            ragflow_client._client.delete_datasets(ids=[datasets[0].id])
            print(f"  ✓ Deleted dataset: {dataset_name}")
    except Exception as e:
        print(f"  ✗ Cleanup failed: {e}")


# =============================================================================
# Agent Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def agent_registry():
    """Get the agent registry with all registered agents"""
    from agents.registry import get_registry
    return get_registry()


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
def context():
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
