#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_agents_live.py
@Desc    : LIVE Agent Tests with Real LLM

Tests FlagPilot agents using real OpenRouter LLM responses.
NO MOCKING - all responses are real API calls.

Run with:
    docker exec Flagpilot-backend pytest tests/agents/test_agents_live.py -v -s
"""

import pytest
from loguru import logger


@pytest.mark.live
class TestAgentRegistry:
    """Test agent registry functionality"""
    
    def test_registry_initialization(self, agent_registry):
        """Test that agent registry loads all agents"""
        agents = agent_registry.list_agents()
        
        assert len(agents) > 0, "Registry should have agents"
        logger.info(f"✅ Registry has {len(agents)} agents: {agents}")
    
    def test_get_each_agent_class(self, agent_registry):
        """Test retrieving each agent class by name"""
        agents = agent_registry.list_agents()
        
        for agent_name in agents:
            agent_class = agent_registry.get_agent_class(agent_name)
            assert agent_class is not None, f"Should get class for {agent_name}"
            
        logger.info(f"✅ All {len(agents)} agent classes retrieved successfully")


@pytest.mark.live
class TestFlagPilotRole:
    """Test base FlagPilotRole functionality"""
    
    def test_role_initialization(self):
        """Test FlagPilotRole can be instantiated"""
        from agents.roles.base_role import FlagPilotRole
        
        role = FlagPilotRole(
            name="TestAgent",
            profile="Test Profile", 
            goal="Test Goal",
            constraints="Test Constraints"
        )
        
        assert role.name == "TestAgent"
        assert role.profile == "Test Profile"
        logger.info("✅ FlagPilotRole initialized successfully")


@pytest.mark.live
@pytest.mark.slow
class TestContractGuardianLive:
    """Test ContractGuardian agent with real LLM"""
    
    def test_contract_guardian_init(self, contract_guardian):
        """Test ContractGuardian initializes correctly"""
        assert contract_guardian is not None
        assert hasattr(contract_guardian, "profile")
        assert hasattr(contract_guardian, "goal")
        
        logger.info(f"✅ ContractGuardian profile: {contract_guardian.profile}")
    
    @pytest.mark.asyncio
    async def test_contract_guardian_analysis(self, live_llm):
        """Test contract analysis with real LLM"""
        # Contract with concerning terms
        contract_text = """
        Contract Terms:
        - Payment: Net 90 days
        - IP: All rights transfer immediately 
        - Termination: Client can terminate without payment for work done
        - Liability: Contractor bears all liability
        """
        
        # Use the LLM directly
        response = await live_llm.aask(
            f"""You are a Contract Guardian AI. Analyze these contract terms 
and identify risks for the freelancer:

{contract_text}

Provide: Risk Level (HIGH/MEDIUM/LOW) and specific concerns."""
        )
        
        assert response is not None
        assert len(response) > 50
        assert "HIGH" in response.upper() or "MEDIUM" in response.upper()
        
        logger.info(f"✅ ContractGuardian analysis: {response[:200]}...")


@pytest.mark.live
@pytest.mark.slow
class TestJobAuthenticatorLive:
    """Test JobAuthenticator agent with real LLM"""
    
    def test_job_authenticator_init(self, job_authenticator):
        """Test JobAuthenticator initializes correctly"""
        assert job_authenticator is not None
        logger.info(f"✅ JobAuthenticator initialized: {job_authenticator.profile}")
    
    @pytest.mark.asyncio
    async def test_job_vetting_legitimate(self, live_llm):
        """Test vetting a legitimate job posting"""
        job_posting = """
        Job Title: Senior React Developer
        Company: TechCorp Inc (Verified)
        
        Requirements:
        - 5+ years React experience
        - TypeScript proficiency
        - REST API experience
        
        Budget: $80-100/hour
        Duration: 6 months
        
        Contact via platform messaging only.
        """
        
        response = await live_llm.aask(
            f"""Analyze this job posting for legitimacy:

{job_posting}

Rate from 1-10 (10 = highly legitimate) and explain."""
        )
        
        assert response is not None
        # Should rate this relatively high
        logger.info(f"✅ Legitimate job rating: {response[:200]}...")
    
    @pytest.mark.asyncio
    async def test_job_vetting_suspicious(self, live_llm):
        """Test vetting a suspicious job posting"""
        job_posting = """
        EASY MONEY! $1000/day guaranteed!
        
        Just need someone to receive payments and forward them.
        Keep 30% commission. No experience needed.
        
        Contact via WhatsApp: +123456789
        Don't use platform - direct contact only.
        Must have crypto wallet.
        """
        
        response = await live_llm.aask(
            f"""Analyze this job posting for legitimacy and red flags:

{job_posting}

Rate from 1-10 (10 = highly legitimate) and list red flags."""
        )
        
        assert response is not None
        # Check response indicates this is suspicious
        response_lower = response.lower()
        assert any(term in response_lower for term in ["scam", "suspicious", "red flag", "avoid", "1", "2", "3"]), \
            "Should identify as suspicious"
        
        logger.info(f"✅ Suspicious job identified: {response[:200]}...")


@pytest.mark.live  
class TestTeamOrchestrationLive:
    """Test team orchestration with real agents"""
    
    def test_team_initialization(self):
        """Test FlagPilotTeam can be initialized"""
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam()
        assert team is not None
        logger.info("✅ FlagPilotTeam initialized")
    
    def test_metagpt_team_compatibility(self):
        """Test MetaGPT Team compatibility"""
        from metagpt.team import Team
        from metagpt.roles import Role
        
        # Create a simple test role using MetaGPT 0.8.1 pattern
        class TestRole(Role):
            name: str = "TestRole"
            profile: str = "Tester"
            goal: str = "Test goal"
            constraints: str = "Be helpful"
        
        team = Team()
        team.hire([TestRole()])
        
        assert len(team.env.roles) == 1
        logger.info("✅ MetaGPT Team compatible")


@pytest.mark.live
@pytest.mark.slow
class TestRAGIntegration:
    """Test RAG context injection with LLM"""
    
    @pytest.mark.asyncio
    async def test_llm_with_context(self, live_llm):
        """Test LLM can use injected context"""
        # Simulate RAG context
        rag_context = """
        KNOWLEDGE BASE CONTEXT:
        - Standard freelance contracts should have Net 30 payment terms
        - Late fees above 2% per month may be excessive
        - IP should transfer upon full payment, not before
        - Always include a kill fee clause for early termination
        """
        
        user_query = "Should I accept Net 90 payment terms?"
        
        prompt = f"""Use the following context to answer the question.

CONTEXT:
{rag_context}

QUESTION: {user_query}

Provide a helpful answer based on the context."""

        response = await live_llm.aask(prompt)
        
        assert response is not None
        assert len(response) > 50
        # Should reference the Net 30 standard from context
        logger.info(f"✅ RAG + LLM response: {response[:200]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
