import pytest
import os
import asyncio
import time
from agents.team import FlagPilotTeam
from ragflow.client import get_ragflow_client
from loguru import logger
from config import settings

# Ensure strict configuration
settings.configure_metagpt_env()

@pytest.mark.asyncio
async def test_simple_greeting_bypass():
    """
    Test that a simple greeting bypasses the heavy multi-agent workflow.
    The Orchestrator should recognize "Hi" and return a direct response.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
         pytest.skip("OpenRouter Key missing")

    logger.info("TEST: Simple Greeting Bypass")
    
    start_time = time.time()
    
    team = FlagPilotTeam()
    # Simple greeting task
    task = "Hi, are you working?"
    context = {"id": "test_greeting_user"}
    
    result = await team.run(task, context)
    
    duration = time.time() - start_time
    logger.info(f"Greeting took {duration:.2f}s")
    
    # Assertions
    # 1. It should be fast (e.g. < 5-8 seconds depending on LLM latency, but faster than full team)
    # 2. 'final_synthesis' should contain a greeting
    # 3. 'agent_outputs' might be empty or minimal if orchestrator handled it directly
    
    synthesis = result.get("final_synthesis", "").lower()
    assert "flagpilot" in synthesis or "help" in synthesis or "working" in synthesis
    
    # Check that we didn't trigger expensive sub-agents for a simple "Hi"
    # (This depends on Orchestrator logic; if it assigns a 'greeter' agent, that's fine,
    # but it shouldn't assign 'contract-guardian')
    agent_outputs = result.get("agent_outputs", {})
    assert "contract-guardian" not in agent_outputs
    assert "risk-advisor" not in agent_outputs

@pytest.mark.asyncio
async def test_context_isolation():
    """
    STRESS TEST: Context Isolation
    Verify that RAG data from User A does not bleed into User B.
    """
    if not os.getenv("RAGFLOW_API_KEY"):
        pytest.skip("RAGFlow Key missing")

    logger.info("TEST: Context Isolation")
    client = get_ragflow_client()
    
    # Setup User A
    user_a = f"user_a_{int(time.time())}"
    doc_a = "Secret Project Alpha: The launch code is BLUE777."
    await client.add_user_document(user_a, doc_a.encode('utf-8'), "alpha_project.txt")
    
    # Setup User B
    user_b = f"user_b_{int(time.time())}"
    doc_b = "Secret Project Beta: The launch code is RED999."
    await client.add_user_document(user_b, doc_b.encode('utf-8'), "beta_project.txt")
    
    # Wait for indexing
    logger.info("Waiting for indexing...")
    await asyncio.sleep(8) 
    
    # Test 1: User A asks for Alpha (Should find)
    team_a = FlagPilotTeam(agents=["profile-analyzer"]) # Use a generic agent that reads context
    res_a = await team_a.run("What is the launch code for Project Alpha?", context={"id": user_a})
    synthesis_a = str(res_a.get("final_synthesis", "")).lower() + str(res_a.get("agent_outputs", ""))
    
    # Test 2: User B asks for Alpha (Should NOT find or fail to know)
    team_b = FlagPilotTeam(agents=["profile-analyzer"])
    res_b = await team_b.run("What is the launch code for Project Alpha?", context={"id": user_b})
    synthesis_b = res_b.get("final_synthesis", "") + str(res_b.get("agent_outputs", ""))
    
    logger.info(f"User A Result: {synthesis_a[:100]}...")
    logger.info(f"User B Result: {synthesis_b[:100]}...")
    
    assert "blue777" in synthesis_a.lower(), "User A failed to retrieve their own secret"
    assert "blue777" not in synthesis_b.lower(), "SECURITY FAILURE: User B access User A's secret!"

@pytest.mark.asyncio
async def test_complex_multistep_workflow():
    """
    STRESS TEST: Complex Multi-step Workflow
    Task: Analyze a contract AND draft an email AND check for scams.
    This forces the Orchestrator to decompose the task and hire multiple agents.
    """
    logger.info("TEST: Complex Multi-step Workflow")
    
    user_id = f"complex_user_{int(time.time())}"
    
    # Simulate a contract context
    bad_contract = """
    AGREEMENT
    Client: FakeCorp
    Terms: You pay us $500 security deposit for equipment via Zelle.
    """
    client = get_ragflow_client()
    if os.getenv("RAGFLOW_API_KEY"):
        await client.add_user_document(user_id, bad_contract.encode('utf-8'), "job_offer.txt")
        await asyncio.sleep(5)
    
    task = """
    I received this job offer. 
    1. Is it a scam? 
    2. Review the payment terms.
    3. Draft a polite email declining it.
    """
    
    team = FlagPilotTeam()
    result = await team.run(task, context={"id": user_id})
    
    agent_outputs = result.get("agent_outputs", {})
    synthesis = result.get("final_synthesis", "")
    
    logger.info(f"Agents used: {list(agent_outputs.keys())}")
    
    # 1. Expect multiple agents or at least key capabilities
    # 'risk-advisor' OR 'job-authenticator' (Scam check)
    # 'contract-guardian' (Terms)
    # 'communication-coach' (Email draft)
    
    # Flexible assertion: expecting at least 2 distinct agents for such a varied task
    assert len(agent_outputs) >= 2, f"Expected multi-agent collaboration, used only: {agent_outputs.keys()}"
    
    output_text = (synthesis + str(agent_outputs)).lower()
    
    # 2. Verify Scam Detection
    assert "scam" in output_text or "fake" in output_text or "zelle" in output_text
    
    # 3. Verify Email Draft
    assert "subject:" in output_text or "dear" in output_text
