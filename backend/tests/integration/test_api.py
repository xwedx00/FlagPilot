#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_api.py
@Desc    : API endpoint tests (LIVE)

Tests API endpoints with real backend.
"""

import pytest
from fastapi.testclient import TestClient
from loguru import logger


@pytest.mark.live
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from main import app
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test GET / returns API info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["version"] == "4.0.0"
        assert "endpoints" in data
        logger.info(f"✅ Root endpoint: v{data['version']}, {data['agents']} agents")
    
    def test_health_endpoint(self, client):
        """Test GET /health returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert len(data["agents"]) > 0
        logger.info(f"✅ Health check: {data['status']}, {len(data['agents'])} agents")


@pytest.mark.live
class TestAgentEndpoints:
    """Test agent API endpoints"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_list_agents(self, client):
        """Test GET /api/agents returns agent list"""
        response = client.get("/api/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] > 0
        assert len(data["agents"]) == data["count"]
        logger.info(f"✅ Listed {data['count']} agents")
    
    def test_get_agent_details(self, client):
        """Test GET /api/agents/{id} returns agent details"""
        # Get first agent
        list_response = client.get("/api/agents")
        agents = list_response.json()["agents"]
        
        if agents:
            agent_id = agents[0]
            response = client.get(f"/api/agents/{agent_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == agent_id
            assert "profile" in data
            logger.info(f"✅ Agent details: {data['name']} - {data['profile']}")
    
    def test_get_nonexistent_agent(self, client):
        """Test 404 for nonexistent agent"""
        response = client.get("/api/agents/nonexistent_xyz")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
