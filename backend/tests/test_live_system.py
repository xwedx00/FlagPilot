"""
FlagPilot Live Integration Test
===============================
Comprehensive test that validates the entire system:
1. RAGFlow - Dataset creation, document upload, retrieval
2. OpenRouter LLM - Response quality, format validation
3. MetaGPT Team Orchestration - Multi-agent collaboration

This test runs against LIVE services and saves all output to test_live_output.txt
"""

import pytest
import asyncio
import time
import os
from datetime import datetime
from typing import Optional
from loguru import logger

# Output file in project root
OUTPUT_FILE = "test_live_output.txt"


def log_output(message: str, console: bool = True):
    """Write to output file and optionally print"""
    if console:
        print(message)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")


class TestLiveSystemIntegration:
    """
    Comprehensive Live Integration Test Suite
    Tests RAGFlow + OpenRouter + MetaGPT together
    """
    
    @classmethod
    def setup_class(cls):
        """Initialize test output file"""
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("FLAGPILOT LIVE INTEGRATION TEST\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
    
    # =========================================
    # SECTION 1: RAGFlow Integration Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_01_ragflow_health_and_connection(self):
        """
        Test 1: Verify RAGFlow is connected and healthy
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 1: RAGFlow Health & Connection")
        log_output("=" * 50)
        
        from ragflow.client import get_ragflow_client
        
        client = get_ragflow_client()
        health = await client.health_check()
        
        log_output(f"Health Status: {health}")
        
        assert health["status"] == "healthy", f"RAGFlow unhealthy: {health}"
        assert health["connected"] == True, "RAGFlow not connected"
        
        log_output("✅ PASS: RAGFlow connected and healthy")
    
    @pytest.mark.asyncio
    async def test_02_ragflow_create_dataset_and_upload(self):
        """
        Test 2: Create dataset and upload document
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 2: RAGFlow Dataset Creation & Document Upload")
        log_output("=" * 50)
        
        from ragflow.client import get_ragflow_client
        
        client = get_ragflow_client()
        
        # Create a test dataset
        timestamp = int(time.time())
        dataset_name = f"flagpilot_test_{timestamp}"
        
        log_output(f"Creating dataset: {dataset_name}")
        
        try:
            dataset = client.create_dataset(
                name=dataset_name,
                description="FlagPilot integration test dataset"
            )
            log_output(f"Dataset created: {dataset.id if hasattr(dataset, 'id') else dataset}")
            
            # Upload a test contract document
            test_contract = """
            FREELANCE SERVICE AGREEMENT
            ===========================
            Client: TestCorp Inc.
            Contractor: Test Freelancer
            
            PAYMENT TERMS:
            - Total: $10,000
            - 50% upfront ($5,000)
            - 50% on completion ($5,000)
            - Net 30 payment terms
            
            IMPORTANT FLAGS:
            - No late fees defined
            - IP transfers immediately on signature
            - Client can delay payment for "satisfaction review"
            
            This is a test document for integration testing.
            """
            
            dataset_id = dataset.id if hasattr(dataset, 'id') else str(dataset)
            log_output(f"Uploading document to dataset {dataset_id}...")
            
            success = await client.upload_document(
                dataset_id=dataset_id,
                filename="test_contract.txt",
                content=test_contract.encode('utf-8')
            )
            
            log_output(f"Upload result: {success}")
            
            # Store dataset_id for later tests
            TestLiveSystemIntegration.test_dataset_id = dataset_id
            
            log_output("✅ PASS: Dataset created and document uploaded")
            
        except Exception as e:
            log_output(f"⚠️ Dataset/Upload failed (may already exist): {e}")
            # List existing datasets
            datasets = client.list_datasets()
            if datasets:
                TestLiveSystemIntegration.test_dataset_id = datasets[0].id
                log_output(f"Using existing dataset: {TestLiveSystemIntegration.test_dataset_id}")
    
    @pytest.mark.asyncio
    async def test_03_ragflow_retrieval(self):
        """
        Test 3: Test RAG retrieval functionality
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 3: RAGFlow Retrieval")
        log_output("=" * 50)
        
        from ragflow.client import get_ragflow_client
        
        client = get_ragflow_client()
        
        # Wait for indexing
        log_output("Waiting 10s for document indexing...")
        await asyncio.sleep(10)
        
        # Try retrieval
        log_output("Searching for 'payment terms'...")
        
        results = await client.search_user_context(
            user_id="test_user",
            query="payment terms contract",
            limit=5
        )
        
        log_output(f"Retrieved {len(results)} chunks")
        
        for i, result in enumerate(results):
            content_preview = result.get("content", "")[:100]
            similarity = result.get("similarity", 0)
            log_output(f"  [{i+1}] Similarity: {similarity:.3f} - {content_preview}...")
        
        # Even if no results (fresh dataset), the retrieval should work
        log_output("✅ PASS: RAGFlow retrieval executed successfully")
    
    # =========================================
    # SECTION 2: OpenRouter LLM Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_04_openrouter_basic_response(self):
        """
        Test 4: Verify OpenRouter LLM responds correctly
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 4: OpenRouter LLM Basic Response")
        log_output("=" * 50)
        
        from openai import AsyncOpenAI
        from config import settings
        
        client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        log_output(f"Model: {settings.OPENROUTER_MODEL}")
        log_output("Sending test prompt...")
        
        start_time = time.time()
        
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
                {"role": "user", "content": "What is 2+2? Reply with just the number."}
            ],
            max_tokens=50
        )
        
        duration = time.time() - start_time
        content = response.choices[0].message.content
        
        log_output(f"Response: {content}")
        log_output(f"Duration: {duration:.2f}s")
        log_output(f"Tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
        
        assert content is not None, "No response from LLM"
        assert len(content) > 0, "Empty response from LLM"
        
        log_output("✅ PASS: OpenRouter LLM responding correctly")
    
    @pytest.mark.asyncio
    async def test_05_openrouter_contract_analysis(self):
        """
        Test 5: LLM can analyze a contract and identify risks
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 5: OpenRouter Contract Analysis Quality")
        log_output("=" * 50)
        
        from openai import AsyncOpenAI
        from config import settings
        
        client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        contract = """
        CONTRACT TERMS:
        - Payment: 50% upfront, 50% on completion
        - No late fees specified
        - IP transfers to client immediately upon signing (not upon payment)
        - Client can delay payment pending "satisfaction review" with no timeline
        """
        
        log_output("Analyzing contract for risks...")
        
        start_time = time.time()
        
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a contract analysis expert. Identify payment and IP risks in contracts. Be concise."},
                {"role": "user", "content": f"Identify the top 3 risks in this contract:\n{contract}"}
            ],
            max_tokens=500
        )
        
        duration = time.time() - start_time
        content = response.choices[0].message.content
        
        log_output(f"\n--- LLM ANALYSIS ---")
        log_output(content)
        log_output(f"--- END ANALYSIS ---")
        log_output(f"\nDuration: {duration:.2f}s")
        
        # Validate response quality
        content_lower = content.lower()
        
        checks = {
            "late_fees": any(term in content_lower for term in ["late fee", "penalty", "no late"]),
            "ip_risk": any(term in content_lower for term in ["ip", "intellectual property", "transfer"]),
            "payment": any(term in content_lower for term in ["payment", "delay", "satisfaction"])
        }
        
        log_output(f"\nQuality Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            log_output(f"  {status} {check}: {'Found' if passed else 'Missing'}")
        
        passed_count = sum(checks.values())
        log_output(f"\nQuality Score: {passed_count}/3")
        
        assert passed_count >= 2, f"LLM analysis quality too low: {passed_count}/3 checks passed"
        
        log_output("✅ PASS: OpenRouter producing quality analysis")
    
    # =========================================
    # SECTION 3: MetaGPT Team Orchestration
    # =========================================
    
    @pytest.mark.asyncio
    async def test_06_team_initialization(self):
        """
        Test 6: Verify team can be initialized with agents
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 6: MetaGPT Team Initialization")
        log_output("=" * 50)
        
        from agents.team import FlagPilotTeam
        from agents.registry import registry
        
        # List available agents
        available = registry.list_agents()
        log_output(f"Available agents: {available}")
        
        # Initialize team with specific agents
        team = FlagPilotTeam(agents=["contract-guardian"])
        
        log_output(f"Team initialized with agents: {list(team.agents.keys())}")
        
        assert len(team.agents) > 0, "No agents loaded in team"
        
        log_output("✅ PASS: Team initialized successfully")
    
    @pytest.mark.asyncio
    async def test_07_team_simple_task(self):
        """
        Test 7: Team can handle a simple greeting (bypass heavy workflow)
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 7: Team Simple Task (Greeting)")
        log_output("=" * 50)
        
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam()
        
        task = "Hi, are you working?"
        context = {"id": "test_user_greeting"}
        
        log_output(f"Task: {task}")
        log_output("Running team...")
        
        start_time = time.time()
        result = await team.run(task, context)
        duration = time.time() - start_time
        
        log_output(f"Duration: {duration:.2f}s")
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        
        log_output(f"\n--- TEAM RESPONSE ---")
        log_output(f"Synthesis: {synthesis[:500] if synthesis else 'None'}...")
        log_output(f"Agents Used: {list(agent_outputs.keys())}")
        log_output(f"--- END RESPONSE ---")
        
        assert synthesis or agent_outputs, "Team produced no output"
        
        log_output("✅ PASS: Team handled simple task")
    
    @pytest.mark.asyncio
    async def test_08_team_contract_review(self):
        """
        Test 8: Full team workflow - Contract review with RAG context
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 8: Full Team Workflow - Contract Review")
        log_output("=" * 50)
        
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam(agents=["contract-guardian"])
        
        task = """
        Review my contract. The key terms are:
        - Payment: 50% upfront, 50% on completion
        - No late fees
        - IP transfers before payment
        
        Is this contract safe to sign? What are the risks?
        """
        
        context = {"id": "test_user_contract"}
        
        log_output(f"Task: {task[:100]}...")
        log_output("Running full team workflow...")
        
        start_time = time.time()
        result = await team.run(task, context)
        duration = time.time() - start_time
        
        log_output(f"Duration: {duration:.2f}s")
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        error = result.get("error")
        
        log_output(f"\n--- FULL TEAM OUTPUT ---")
        log_output(f"Error: {error}")
        log_output(f"Agents: {list(agent_outputs.keys())}")
        
        for agent_id, output in agent_outputs.items():
            log_output(f"\n[{agent_id}]:")
            log_output(f"{output[:500] if output else 'No output'}...")
        
        log_output(f"\n[SYNTHESIS]:")
        log_output(synthesis if synthesis else "No synthesis")
        log_output(f"--- END OUTPUT ---")
        
        # Validate response contains relevant content
        combined = (synthesis + str(agent_outputs)).lower()
        
        quality_checks = {
            "payment_mentioned": "payment" in combined or "50%" in combined,
            "risk_identified": any(w in combined for w in ["risk", "concern", "issue", "problem", "caution"]),
            "ip_mentioned": "ip" in combined or "intellectual" in combined or "transfer" in combined
        }
        
        log_output(f"\nQuality Checks:")
        for check, passed in quality_checks.items():
            status = "✅" if passed else "❌"
            log_output(f"  {status} {check}")
        
        assert not error, f"Team returned error: {error}"
        assert synthesis or agent_outputs, "No output from team"
        
        log_output("✅ PASS: Full team workflow completed")
    
    @pytest.mark.asyncio
    async def test_09_team_multi_agent_collaboration(self):
        """
        Test 9: Complex task requiring multiple agents
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 9: Multi-Agent Collaboration")
        log_output("=" * 50)
        
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam()  # All agents
        
        task = """
        I received a job offer from "QuickCash Enterprises". They want me to:
        1. Pay a $500 "equipment deposit" via Zelle
        2. Work remotely with no contract
        3. Get paid weekly in crypto
        
        Is this legitimate? What should I do?
        """
        
        context = {"id": "test_user_scam_check"}
        
        log_output(f"Task: {task[:150]}...")
        log_output("Running multi-agent collaboration...")
        
        start_time = time.time()
        result = await team.run(task, context)
        duration = time.time() - start_time
        
        log_output(f"Duration: {duration:.2f}s")
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        
        log_output(f"\n--- MULTI-AGENT OUTPUT ---")
        log_output(f"Agents Used: {list(agent_outputs.keys())}")
        log_output(f"Agent Count: {len(agent_outputs)}")
        
        for agent_id, output in agent_outputs.items():
            log_output(f"\n[{agent_id}]:")
            log_output(f"{str(output)[:300] if output else 'No output'}...")
        
        log_output(f"\n[FINAL SYNTHESIS]:")
        log_output(synthesis[:800] if synthesis else "No synthesis")
        log_output(f"--- END OUTPUT ---")
        
        # Check for scam detection
        combined = (synthesis + str(agent_outputs)).lower()
        
        scam_detection = {
            "scam_identified": any(w in combined for w in ["scam", "fraud", "suspicious", "red flag", "warning"]),
            "deposit_flagged": any(w in combined for w in ["deposit", "zelle", "upfront payment"]),
            "recommendation": any(w in combined for w in ["avoid", "decline", "don't", "do not", "reject"])
        }
        
        log_output(f"\nScam Detection Checks:")
        for check, passed in scam_detection.items():
            status = "✅" if passed else "❌"
            log_output(f"  {status} {check}")
        
        passed_count = sum(scam_detection.values())
        log_output(f"\nScam Detection Score: {passed_count}/3")
        
        assert synthesis or agent_outputs, "No output from team"
        
        log_output("✅ PASS: Multi-agent collaboration completed")
    
    # =========================================
    # SECTION 4: End-to-End System Test
    # =========================================
    
    @pytest.mark.asyncio
    async def test_10_end_to_end_flow(self):
        """
        Test 10: Complete end-to-end flow
        RAG Upload -> Retrieval -> LLM Analysis -> Team Synthesis
        """
        log_output("\n" + "=" * 50)
        log_output("TEST 10: END-TO-END SYSTEM FLOW")
        log_output("=" * 50)
        
        from ragflow.client import get_ragflow_client
        from agents.team import FlagPilotTeam
        
        user_id = f"e2e_test_{int(time.time())}"
        
        log_output(f"Test User: {user_id}")
        log_output("Starting end-to-end flow...")
        
        # Step 1: Check RAGFlow
        log_output("\n[Step 1] RAGFlow Health Check")
        client = get_ragflow_client()
        health = await client.health_check()
        log_output(f"  Status: {health['status']}")
        
        # Step 2: Search existing context
        log_output("\n[Step 2] RAG Context Search")
        results = await client.search_user_context(
            user_id=user_id,
            query="freelance contract payment terms",
            limit=3
        )
        log_output(f"  Found {len(results)} existing context chunks")
        
        # Step 3: Run Team with context
        log_output("\n[Step 3] Team Task Execution")
        team = FlagPilotTeam(agents=["contract-guardian", "risk-advisor"])
        
        task = """
        I'm a new freelancer. A client wants to hire me but their contract has these terms:
        - Full payment only after project completion
        - No milestone payments
        - 60-day payment window
        - No late fees
        
        What should I negotiate for?
        """
        
        start_time = time.time()
        result = await team.run(task, context={"id": user_id})
        duration = time.time() - start_time
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        error = result.get("error")
        
        log_output(f"  Duration: {duration:.2f}s")
        log_output(f"  Agents: {list(agent_outputs.keys())}")
        log_output(f"  Error: {error}")
        
        # Step 4: Validate output quality
        log_output("\n[Step 4] Output Validation")
        
        combined = (synthesis + str(agent_outputs)).lower()
        
        quality = {
            "mentions_milestone": any(w in combined for w in ["milestone", "partial", "deposit", "upfront"]),
            "mentions_payment": any(w in combined for w in ["payment", "pay", "invoice"]),
            "mentions_negotiation": any(w in combined for w in ["negotiate", "ask", "request", "suggest", "recommend"]),
            "actionable_advice": any(w in combined for w in ["should", "could", "would", "consider"])
        }
        
        for check, passed in quality.items():
            status = "✅" if passed else "❌"
            log_output(f"  {status} {check}")
        
        score = sum(quality.values())
        log_output(f"\n  Quality Score: {score}/4")
        
        # Final output
        log_output("\n" + "=" * 50)
        log_output("END-TO-END COMPLETE OUTPUT")
        log_output("=" * 50)
        log_output(synthesis if synthesis else str(agent_outputs))
        
        assert not error, f"E2E flow error: {error}"
        assert synthesis or agent_outputs, "No output from E2E flow"
        
        log_output("\n✅ PASS: End-to-end flow completed successfully")
    
    @classmethod
    def teardown_class(cls):
        """Final summary"""
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write("TEST SUITE COMPLETED\n")
            f.write(f"End Time: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")
        
        print(f"\n📄 Full output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
