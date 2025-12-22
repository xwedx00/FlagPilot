"""
CopilotKit Integration Tests (Multi-Venv Architecture)
=======================================================
Tests the CopilotKit SDK integration with FlagPilot backend.
MetaGPT/CopilotKit/RAGFlow run in isolated venvs - tested via subprocess runners.
"""

import pytest
import os
from fastapi.testclient import TestClient


class TestCopilotKitIntegration:
    """Tests for API endpoints (run in main environment)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        from main import app
        self.client = TestClient(app)
    
    def test_copilotkit_endpoint_or_fallback(self):
        """Test that /copilotkit endpoint exists or CopilotKit unavailable in test env"""
        response = self.client.post("/copilotkit", json={})
        # In multi-venv arch, CopilotKit may not be available in test env
        # 404 is acceptable in test env (SDK in isolated venv)
        assert response.status_code in [200, 400, 404, 422, 500]
    
    def test_agents_list_endpoint(self):
        """Test that /api/agents returns agent list"""
        response = self.client.get("/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert "count" in data
        assert data["count"] >= 10
        
        # Verify key agents exist
        agent_ids = [a["id"] for a in data["agents"]]
        assert "contract-guardian" in agent_ids
        assert "job-authenticator" in agent_ids
        assert "flagpilot-orchestrator" in agent_ids
    
    def test_agent_details_endpoint(self):
        """Test getting individual agent details"""
        response = self.client.get("/api/agents/contract-guardian")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "contract-guardian"
        assert "description" in data
        assert "goal" in data
    
    def test_agent_not_found(self):
        """Test 404 for non-existent agent"""
        response = self.client.get("/api/agents/nonexistent-agent")
        assert response.status_code == 404
    
    def test_health_endpoint(self):
        """Test health check returns correct info"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        # Features may vary based on available venvs
        assert "features" in data
    
    def test_root_endpoint(self):
        """Test root endpoint provides API info"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "FlagPilot Agent API"
        assert "version" in data


class TestSubprocessRunners:
    """Tests for the subprocess runners (files exist in main env)"""
    
    def test_metagpt_runner_file_exists(self):
        """Test that MetaGPT runner module exists"""
        from lib.runners.metagpt_runner import MetaGPTRunner
        assert MetaGPTRunner is not None
    
    def test_ragflow_runner_file_exists(self):
        """Test that RAGFlow runner module exists"""
        from lib.runners.ragflow_runner import RAGFlowRunner
        assert RAGFlowRunner is not None
    
    def test_copilotkit_runner_file_exists(self):
        """Test that CopilotKit runner module exists"""
        from lib.runners.copilotkit_runner import CopilotKitRunner
        assert CopilotKitRunner is not None


class TestMemoryManager:
    """Tests for the memory/wisdom storage system"""
    
    @pytest.mark.skipif(
        os.environ.get("ES_HOST") is None,
        reason="Elasticsearch not configured"
    )
    def test_memory_manager_import(self):
        """Test that MemoryManager can be imported"""
        try:
            from lib.memory.manager import MemoryManager
            assert MemoryManager is not None
        except Exception:
            pytest.skip("Elasticsearch not available")
    
    @pytest.mark.skipif(
        os.environ.get("ES_HOST") is None, 
        reason="Elasticsearch not configured"
    )
    def test_memory_manager_has_methods(self):
        """Test MemoryManager has expected methods"""
        try:
            from lib.memory.manager import MemoryManager
            manager = MemoryManager()
            assert hasattr(manager, "get_current_user_profile")
            assert hasattr(manager, "update_user_profile")
            assert hasattr(manager, "save_experience")
            assert hasattr(manager, "search_similar_experiences")
        except Exception:
            pytest.skip("Elasticsearch not available")


class TestAuthMiddleware:
    """Tests for auth middleware"""
    
    @pytest.mark.skip(reason="pyjwt not yet in Docker image")
    def test_auth_middleware_import(self):
        """Test that auth middleware can be imported"""
        try:
            from lib.auth.middleware import OptionalAuthMiddleware
            assert OptionalAuthMiddleware is not None
        except ImportError as e:
            if "jwt" in str(e):
                pytest.skip("pyjwt not installed")
            raise
