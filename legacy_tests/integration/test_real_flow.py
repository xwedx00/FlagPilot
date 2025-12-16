import pytest
import time
import os
import asyncio
from agents.team import FlagPilotTeam
from ragflow.client import get_ragflow_client
from loguru import logger
from config import settings

# Real context data from the user's test_data folder (inlined for reliability)
CONTRACT_CONTENT = """
FREELANCE SERVICE AGREEMENT
===========================

Client: TechStartup Solutions LLC ("Client")
Contractor: [YOUR NAME] ("Contractor")
Date: December 1, 2025
Project: Full-Stack Web Application Development

1. SCOPE OF WORK
----------------
Contractor agrees to develop a complete web application including:
- Frontend React/Next.js application
- Backend API with Python/FastAPI
- Database design and implementation (PostgreSQL)
- User authentication system
- Payment integration (Stripe)
- Admin dashboard

2. TIMELINE
-----------
Project Start: December 5, 2025
Milestone 1 (MVP): January 15, 2025 - $5,000 upon completion
Milestone 2 (Beta): February 15, 2025 - $5,000 upon completion
Final Delivery: March 1, 2025 - $5,000 upon completion

3. PAYMENT TERMS
----------------
Total Project Value: $15,000 USD
Payment Schedule: 50% upfront ($7,500), 50% upon completion ($7,500)
Payment Method: Bank transfer within 30 days of invoice

IMPORTANT: No late fees specified.
IMPORTANT: Client has right to delay payment pending "satisfaction review" - timeline undefined.
IMPORTANT: IP transfer occurs immediately upon signature, not upon final payment.

4. TERMINATION
--------------
Either party may terminate with 7 days notice.
Upon termination by Client, Contractor receives payment only for "approved deliverables."
"Approved" status determined solely by Client.

5. INTELLECTUAL PROPERTY
------------------------
All work product, including code, designs, and documentation, becomes Client property
upon creation (not upon payment).
"""

@pytest.mark.asyncio
async def test_full_rag_team_integration():
    """
    INTEGRATION TEST: Real connection to RAGFlow and OpenRouter.
    
    Scenario:
    1. User uploads a contract (RAG).
    2. User asks for a risk assessment.
    3. RAG retrieves the contract.
    4. Agents (Contract Guardian) analyze it.
    5. Final response identifies the '50% upfront' and 'No late fees' risks.
    """
    
    # 0. Check Environment & Configure
    # Inject OpenRouter config if present
    settings.configure_metagpt_env()
    
    # If keys are still missing, skip
    if not os.getenv("RAGFLOW_API_KEY") or (not os.getenv("OPENAI_API_KEY") and not os.getenv("OPENROUTER_API_KEY")):
        pytest.skip("Skipping integration test: RAGFLOW_API_KEY or OPEN_ROUTER_API_KEY not set")

    # 1. Setup User & RAG
    # Use a dynamic ID to avoid collisions in RAGFlow
    user_id = f"integ_user_{int(time.time())}"
    client = get_ragflow_client()
    
    assert client.is_connected, "RAGFlow client failed to connect"
    
    logger.info(f"Starting Integration Test for User: {user_id}")
    
    # 2. Upload Document
    logger.info("Uploading contract document...")
    success = await client.add_user_document(
        user_id=user_id,
        content=CONTRACT_CONTENT.encode('utf-8'),
        filename="contract.txt"
    )
    assert success, "Failed to upload document to RAGFlow"
    
    # 3. Wait for Parsing/Indexing
    # RAGFlow parsing can take a moment. We poll for it.
    logger.info("Waiting for RAGFlow indexing (sleeping 10s)...")
    await asyncio.sleep(10)
    
    # 4. Verify Retrieval (Sanity Check)
    logger.info("Verifying retrieval...")
    chunks = await client.search_user_context(user_id, "payment terms", limit=3)
    if not chunks:
         logger.warning("Retrieval returned empty! Waiting another 10s...")
         await asyncio.sleep(10)
         chunks = await client.search_user_context(user_id, "payment terms", limit=3)
    
    assert len(chunks) > 0, "RAGFlow failed to index/retrieve the document chunks"
    retrieved_text = str(chunks).lower()
    assert "50% upfront" in retrieved_text or "7,500" in retrieved_text
    
    # 5. Run FlagPilot Team
    logger.info("Running FlagPilot Team...")
    
    task_prompt = """
    Review this contract. 
    1. Is it a scam? Use the uploaded contract context.
    2. What are the payment terms?
    3. Are there late fees?
    """
    
    # Initialize team (agents will successfully utilize RAG context if injected)
    team = FlagPilotTeam(agents=["contract-guardian"])
    
    # Context dictionary contains the user_id, which FlagPilotTeam uses to query RAG
    result = await team.run(task_prompt, context={"id": user_id})
    
    # 6. Analyze Results
    logger.info(f"Team Result: {result}")
    
    if result.get("error"):
        pytest.fail(f"Team execution returned error: {result['error']}")

    agent_outputs = result.get("agent_outputs", {})
    final_synthesis = result.get("final_synthesis") or ""
    
    # If orchestrator ran properly, we should have a synthesis or at least agent output
    assert final_synthesis or agent_outputs
    
    combined_output = (final_synthesis + str(agent_outputs)).lower()
    
    # Assertions on content (proving RAG was used)
    # The Model should find the specific facts from the contract
    assert "50%" in combined_output or "7,500" in combined_output, "Agent failed to find payment amount"
    assert "late fees" in combined_output, "Agent failed to discuss late fees"
    # assert "techstartup" in combined_output, "Agent failed to identify client name"
    
    logger.info("Integration Test Passed: RAG and LLM connected successfully.")
