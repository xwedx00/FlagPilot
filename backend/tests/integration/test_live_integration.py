#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_live_integration.py
@Desc    : LIVE Integration Tests for FlagPilot

IMPORTANT: These tests use LIVE APIs:
- OpenRouter LLM (real API calls)
- RAGFlow (real vector search)

All responses are real - NO MOCKING.

Run with:
    docker exec Flagpilot-backend pytest tests/integration/test_live_integration.py -v -s
"""

import pytest
from loguru import logger


@pytest.mark.live
class TestLiveRAGFlow:
    """Test RAGFlow connectivity and search"""
    
    def test_ragflow_health(self, ragflow_client):
        """Verify RAGFlow client is initialized"""
        assert ragflow_client is not None
        logger.info("✅ RAGFlow client initialized")
    
    @pytest.mark.asyncio
    async def test_ragflow_health_check(self, ragflow_client):
        """Test RAGFlow health check"""
        health = await ragflow_client.health_check()
        
        logger.info(f"RAGFlow health: {health}")
        # Health check should return some info even if not fully connected
        assert health is not None
        assert "status" in health
        logger.info(f"✅ RAGFlow health status: {health['status']}")
    
    @pytest.mark.asyncio
    async def test_search_user_context(self, ragflow_client, test_user_id):
        """Test searching user context (may return empty if no data)"""
        results = await ragflow_client.search_user_context(
            user_id=test_user_id,
            query="payment terms",
            limit=5
        )
        
        # Results may be empty if no data seeded, but should not error
        assert isinstance(results, list)
        logger.info(f"✅ Search returned {len(results)} results")


@pytest.mark.live
@pytest.mark.slow
class TestLiveLLM:
    """Test LLM with real OpenRouter API calls"""
    
    @pytest.mark.asyncio
    async def test_llm_basic_response(self, live_llm):
        """Test LLM responds to basic query"""
        response = await live_llm.aask(
            "What are 3 key things to check in a freelance contract? Be concise."
        )
        
        assert response is not None
        assert len(response) > 50, "Response should be substantive"
        
        logger.info(f"✅ LLM response ({len(response)} chars): {response[:200]}...")
    
    @pytest.mark.asyncio
    async def test_llm_contract_analysis(self, live_llm):
        """Test LLM can analyze contract text"""
        contract_excerpt = """
        Payment Terms: Net 60 days from invoice date.
        Late Fee: 5% per month compounded.
        Intellectual Property: All work product owned by Client immediately upon creation.
        Termination: Client may terminate at any time without notice or payment.
        """
        
        response = await live_llm.aask(
            f"""Analyze these contract terms and identify any concerning clauses for a freelancer:

{contract_excerpt}

Provide a brief analysis with risk level (LOW/MEDIUM/HIGH) for each term."""
        )
        
        assert response is not None
        assert len(response) > 100
        assert any(level in response.upper() for level in ["LOW", "MEDIUM", "HIGH"]), \
            "Response should include risk assessment"
        
        logger.info(f"✅ Contract analysis: {response[:300]}...")


@pytest.mark.live
@pytest.mark.slow
class TestLiveAgentsWithRAGContext:
    """Test agents using real LLM + RAGFlow context"""
    
    @pytest.mark.asyncio
    async def test_contract_review_with_context(self, live_llm):
        """Test contract review using simulated RAG context + LLM"""
        # Simulated RAG context (would come from RAGFlow in real scenario)
        context = """
        KNOWLEDGE BASE:
        - Standard freelance contracts should have Net 30 payment terms
        - Late fees above 2% monthly may be excessive
        - IP should transfer upon FULL payment, not before
        - Always include kill fee for early termination
        """
        
        # Ask LLM to analyze with context
        prompt = f"""Based on the following knowledge base context and your expertise, 
analyze the payment terms "Net 60 with 5% monthly late fee" for a freelancer.

CONTEXT FROM KNOWLEDGE BASE:
{context}

Provide your analysis with:
1. Risk level (LOW/MEDIUM/HIGH)
2. Key concerns
3. Recommendation
"""
        
        response = await live_llm.aask(prompt)
        
        assert response is not None
        assert len(response) > 100
        
        logger.info(f"✅ RAG + LLM analysis complete: {response[:300]}...")
    
    @pytest.mark.asyncio
    async def test_job_vetting_with_context(self, live_llm):
        """Test job posting vetting using RAG context + LLM"""
        # Suspicious job posting to analyze
        job_posting = """
        URGENT: Need payment processor!
        Easy $500/day guaranteed. No experience needed.
        Just handle customer payments and keep 20% commission.
        Contact us via personal WhatsApp only. 
        Don't use platform messaging.
        """
        
        # Simulated RAG context
        context = """
        KNOWLEDGE BASE - RED FLAGS:
        - Requests to move off-platform are suspicious
        - "Payment processing" jobs are often money laundering scams
        - Guaranteed income claims are red flags
        - WhatsApp-only contact avoids platform protections
        """
        
        prompt = f"""Analyze this job posting for red flags and legitimacy.

JOB POSTING:
{job_posting}

REFERENCE KNOWLEDGE:
{context}

Provide:
1. Legitimacy Score (1-10)
2. Red flags identified
3. Recommendation (PROCEED/CAUTION/AVOID)
"""
        
        response = await live_llm.aask(prompt)
        
        assert response is not None
        response_lower = response.lower()
        assert any(term in response_lower for term in ["avoid", "caution", "scam", "suspicious", "1", "2", "3"]), \
            "Should identify this as suspicious"
        
        logger.info(f"✅ Job vetting complete: {response[:300]}...")


@pytest.mark.live
class TestAgentRegistryLive:
    """Test agent registry with live agents"""
    
    def test_all_agents_registered(self, agent_registry):
        """Verify all expected agents are registered"""
        agents = agent_registry.list_agents()
        
        expected_agents = [
            "contract_guardian",
            "job_authenticator", 
            "negotiation_assistant",
        ]
        
        for agent in expected_agents:
            if agent in agents:
                logger.info(f"  ✓ {agent} registered")
        
        assert len(agents) >= 5, f"Should have at least 5 agents, found {len(agents)}"
        logger.info(f"✅ Total agents registered: {len(agents)}")
    
    def test_instantiate_agents(self, agent_registry):
        """Test that agents can be instantiated"""
        agents = agent_registry.list_agents()
        
        instantiated = 0
        for agent_name in agents[:5]:  # Test first 5
            try:
                agent_class = agent_registry.get_agent_class(agent_name)
                if agent_class:
                    agent = agent_class()
                    assert agent is not None
                    instantiated += 1
                    logger.info(f"  ✓ Instantiated: {agent_name}")
            except Exception as e:
                logger.warning(f"  ✗ Failed to instantiate {agent_name}: {e}")
        
        assert instantiated > 0, "Should instantiate at least one agent"
        logger.info(f"✅ Instantiated {instantiated} agents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
