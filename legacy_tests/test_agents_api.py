"""
Agent Endpoint Tests
====================
Tests for the simplified agent API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import json


class TestAgentEndpoints:
    """Test the /api/agents endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        # Import here to avoid config issues
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from main import app
        self.client = TestClient(app)
    
    def test_list_agents(self):
        """Test GET /api/agents returns list of agents"""
        response = self.client.get("/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert "count" in data
        assert isinstance(data["agents"], list)
        assert data["count"] == len(data["agents"])
        assert data["count"] > 0  # Should have at least some agents
    
    def test_get_agent_details(self):
        """Test GET /api/agents/{agent_id} returns agent details"""
        # First get list of agents
        response = self.client.get("/api/agents")
        agents = response.json()["agents"]
        
        if agents:
            agent_id = agents[0]
            response = self.client.get(f"/api/agents/{agent_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "profile" in data
            assert "goal" in data
    
    def test_get_nonexistent_agent(self):
        """Test GET /api/agents/{agent_id} with invalid ID returns 404"""
        response = self.client.get("/api/agents/nonexistent-agent-xyz")
        assert response.status_code == 404


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from main import app
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test GET /health returns healthy status"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "agents" in data
        assert "features" in data
    
    def test_root_endpoint(self):
        """Test GET / returns API info"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestAgentChatStreaming:
    """Test agent chat streaming endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from main import app
        self.client = TestClient(app)
    
    def test_chat_endpoint_exists(self, mock_llm):
        """Test POST /api/agents/{agent_id}/chat endpoint exists"""
        # Get first available agent
        response = self.client.get("/api/agents")
        agents = response.json()["agents"]
        
        if agents:
            agent_id = agents[0]
            # Just check the endpoint exists and accepts the request
            # Full streaming test requires async client
            response = self.client.post(
                f"/api/agents/{agent_id}/chat",
                json={"message": "Hello", "context": None}
            )
            # Should get streaming response (or at least not 404)
            assert response.status_code != 404
    
    def test_team_chat_endpoint_exists(self, mock_llm):
        """Test POST /api/team/chat endpoint exists"""
        response = self.client.post(
            "/api/team/chat",
            json={"message": "Analyze this contract", "context": None}
        )
        # Should get streaming response (or at least not 404)
        assert response.status_code != 404
