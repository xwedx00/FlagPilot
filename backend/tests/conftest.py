#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : conftest.py
@Desc    : Centralized fixtures for FlagPilot Backend Tests (MetaGPT-Style)
"""

import sys
import os
import pytest
from unittest.mock import MagicMock
from typing import AsyncGenerator

# Ensure backend modules are importable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from metagpt.context import Context
from metagpt.logs import logger
from pydantic import BaseModel
from typing import Optional

# Redefine UserData to avoid importing 'auth' which triggers 'models' (DB)
class UserData(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: str = "user"

# --- standard metagpt fixtures ---

@pytest.fixture(scope="session", autouse=True)
def init_config():
    """Initialize any global config required for the session"""
    # Allow integration tests to bypass mock environment injection
    if os.getenv("SKIP_MOCK_ENV"):
        return

    # Mock environment variables to prevent real API calls if not intended
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    os.environ["OPENAI_API_BASE"] = "http://mock-url"

@pytest.fixture
def mock_llm(mocker):
    """
    Mock the BaseLLM to avoid real API calls.
    Return a mock object that can be configured per test.
    """
    mock_llm = MagicMock()
    mock_llm.aask.return_value = "Mock LLM Response"
    mock_llm.aask_batch.return_value = ["Mock Response 1", "Mock Response 2"]
    
    # Patch the standard import paths for LLM
    mocker.patch("metagpt.provider.base_llm.BaseLLM.aask", side_effect=mock_llm.aask)
    mocker.patch("metagpt.provider.openai_api.OpenAILLM.aask", side_effect=mock_llm.aask)
    
    return mock_llm

@pytest.fixture
def context(mock_llm):
    """
    Provide a fresh MetaGPT Context for each test function.
    """
    ctx = Context()
    # Inject our mock LLM if needed, though patching handles most cases
    return ctx

# --- flagpilot augmented fixtures ---

@pytest.fixture
def mock_user() -> UserData:
    """
    Return a valid UserData object for authenticated context.
    """
    return UserData(
        id="test_user_id",
        email="test@flagpilot.io",
        name="Test User",
        role="admin"
    )

@pytest.fixture
def mock_rag(mocker):
    """
    Mock the RAGFlow client interactions.
    """
    mock_rag_client = MagicMock()
    # Mock common methods like search, add_document
    mock_rag_client.search.return_value = [{"content": "Retrieved content", "score": 0.9}]
    
    # If there's a specific import path for the global rag client, patch it here
    # mocker.patch("backend.lib.rag.get_client", return_value=mock_rag_client)
    
    return mock_rag_client

@pytest.fixture
def authenticated_context(context, mock_user):
    """
    A Context object coming pre-loaded with User Information 
    (mimicking the request scope in FastAPI)
    """
    # In FlagPilot, user info might be stored in the context kwargs or similar
    context.kwargs["user"] = mock_user
    return context
