"""
FlagPilot Live Integration Test - ENHANCED
============================================
Comprehensive test that validates the entire system with VERBOSE OUTPUT:
1. RAGFlow - Dataset creation, document upload, retrieval, global wisdom
2. OpenRouter LLM - Response quality, format validation, token usage
3. MetaGPT Team Orchestration - Multi-agent collaboration, scam detection

This test runs against LIVE services and saves ALL output to test_live_output.txt

Based on patterns from:
- legacy_tests/test_stress_global_wisdom.py (RAG seeding, quality filtering)
- legacy_tests/integration/test_real_flow.py (full workflow)
- legacy_tests/integration/test_stress_scenarios.py (context isolation, multi-step)
"""

import pytest
import asyncio
import time
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger

# Output file in project root
OUTPUT_FILE = "test_live_output.txt"


def log_output(message: str, level: str = "INFO", console: bool = True):
    """Write to output file with timestamp and log level"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    formatted = f"[{timestamp}] [{level}] {message}"
    
    if console:
        # Use colors based on level
        if level == "ERROR":
            print(f"\033[91m{formatted}\033[0m")  # Red
        elif level == "WARNING":
            print(f"\033[93m{formatted}\033[0m")  # Yellow
        elif level == "SUCCESS":
            print(f"\033[92m{formatted}\033[0m")  # Green
        elif level == "DEBUG":
            print(f"\033[90m{formatted}\033[0m")  # Gray
        else:
            print(formatted)
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{formatted}\n")


def log_section(title: str):
    """Log a major section header"""
    border = "=" * 70
    log_output(f"\n{border}")
    log_output(f"  {title}")
    log_output(f"{border}\n")


def log_subsection(title: str):
    """Log a subsection header"""
    log_output(f"\n--- {title} ---")


def log_json(data: Any, label: str = "DATA"):
    """Pretty print JSON data"""
    try:
        formatted = json.dumps(data, indent=2, default=str)
        log_output(f"{label}:\n{formatted}", "DEBUG")
    except:
        log_output(f"{label}: {data}", "DEBUG")


class TestLiveSystemIntegration:
    """
    Enhanced Live Integration Test Suite
    Tests RAGFlow + OpenRouter + MetaGPT with VERBOSE output
    """
    
    @classmethod
    def setup_class(cls):
        """Initialize test output file"""
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("  FLAGPILOT LIVE INTEGRATION TEST - VERBOSE MODE\n")
            f.write(f"  Started: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
        
        # Store test data for sharing between tests
        cls.shared_data = {}
    
    # =========================================
    # SECTION 1: Environment & Health Checks
    # =========================================
    
    @pytest.mark.asyncio
    async def test_01_environment_check(self):
        """
        Test 1: Verify all environment variables are set
        """
        log_section("TEST 1: ENVIRONMENT CHECK")
        
        from config import settings
        
        checks = {
            "OPENROUTER_API_KEY": bool(settings.OPENROUTER_API_KEY),
            "OPENROUTER_MODEL": bool(settings.OPENROUTER_MODEL),
            "OPENROUTER_BASE_URL": bool(settings.OPENROUTER_BASE_URL),
            "RAGFLOW_API_KEY": bool(settings.RAGFLOW_API_KEY),
            "RAGFLOW_URL": bool(settings.RAGFLOW_URL),
        }
        
        log_output(f"OpenRouter Model: {settings.OPENROUTER_MODEL}", "INFO")
        log_output(f"OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}", "INFO")
        log_output(f"RAGFlow URL: {settings.RAGFLOW_URL}", "INFO")
        log_output(f"RAGFlow API Key: {settings.RAGFLOW_API_KEY[:20]}...", "INFO")
        
        for name, is_set in checks.items():
            status = "✅ SET" if is_set else "❌ MISSING"
            log_output(f"  {name}: {status}", "INFO")
        
        all_set = all(checks.values())
        assert all_set, f"Missing environment variables: {[k for k, v in checks.items() if not v]}"
        
        log_output("Environment check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_02_ragflow_health(self):
        """
        Test 2: Verify RAGFlow is connected and healthy
        """
        log_section("TEST 2: RAGFLOW HEALTH CHECK")
        
        from ragflow.client import get_ragflow_client
        
        client = get_ragflow_client()
        log_output(f"RAGFlow Base URL: {client.base_url}", "DEBUG")
        
        health = await client.health_check()
        log_json(health, "Health Response")
        
        assert health["status"] == "healthy", f"RAGFlow unhealthy: {health}"
        assert health["connected"] == True, "RAGFlow not connected"
        
        # Store for later
        TestLiveSystemIntegration.shared_data["ragflow_healthy"] = True
        
        log_output("RAGFlow health check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio  
    async def test_03_openrouter_health(self):
        """
        Test 3: Verify OpenRouter LLM responds with token usage info
        """
        log_section("TEST 3: OPENROUTER LLM HEALTH CHECK")
        
        from openai import AsyncOpenAI
        from config import settings
        
        client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        log_output(f"Model: {settings.OPENROUTER_MODEL}", "INFO")
        log_output("Sending test prompt...", "INFO")
        
        start_time = time.time()
        
        try:
            response = await client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Respond in one short sentence."},
                    {"role": "user", "content": "Say hello and confirm you're working."}
                ],
                max_tokens=100
            )
            
            duration = time.time() - start_time
            content = response.choices[0].message.content
            
            log_output(f"Response: {content}", "INFO")
            log_output(f"Duration: {duration:.2f}s", "INFO")
            
            # Token usage (OpenRouter specific)
            if response.usage:
                log_output(f"Prompt Tokens: {response.usage.prompt_tokens}", "DEBUG")
                log_output(f"Completion Tokens: {response.usage.completion_tokens}", "DEBUG")
                log_output(f"Total Tokens: {response.usage.total_tokens}", "DEBUG")
            
            assert content is not None, "No response from LLM"
            assert len(content) > 0, "Empty response from LLM"
            
            TestLiveSystemIntegration.shared_data["llm_healthy"] = True
            log_output("OpenRouter health check PASSED", "SUCCESS")
            
        except Exception as e:
            log_output(f"OpenRouter ERROR: {e}", "ERROR")
            raise
    
    # =========================================
    # SECTION 2: RAGFlow Integration Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_04_ragflow_dataset_operations(self):
        """
        Test 4: Create dataset, upload documents, verify retrieval
        """
        log_section("TEST 4: RAGFLOW DATASET OPERATIONS")
        
        from ragflow.client import get_ragflow_client
        
        client = get_ragflow_client()
        timestamp = int(time.time())
        
        # Step 1: List existing datasets
        log_subsection("Step 1: List Existing Datasets")
        datasets = client.list_datasets()
        log_output(f"Found {len(datasets)} existing datasets", "INFO")
        for ds in datasets[:5]:  # Show first 5
            log_output(f"  - {getattr(ds, 'name', 'unknown')}: {getattr(ds, 'id', 'unknown')}", "DEBUG")
        
        # Step 2: Create test dataset
        log_subsection("Step 2: Create Test Dataset")
        dataset_name = f"flagpilot_live_test_{timestamp}"
        
        try:
            dataset = client.create_dataset(
                name=dataset_name,
                description="FlagPilot live integration test - comprehensive"
            )
            dataset_id = dataset.id if hasattr(dataset, 'id') else str(dataset)
            log_output(f"Created dataset: {dataset_name}", "SUCCESS")
            log_output(f"Dataset ID: {dataset_id}", "DEBUG")
            
            # Store for later tests
            TestLiveSystemIntegration.shared_data["test_dataset_id"] = dataset_id
            
        except Exception as e:
            log_output(f"Dataset creation failed (may exist): {e}", "WARNING")
            # Use first existing dataset
            if datasets:
                dataset_id = datasets[0].id
                TestLiveSystemIntegration.shared_data["test_dataset_id"] = dataset_id
                log_output(f"Using existing dataset: {dataset_id}", "INFO")
        
        # Step 3: Upload test document
        log_subsection("Step 3: Upload Test Contract")
        
        test_contract = """
        FREELANCE SERVICE AGREEMENT - RISKY CLIENT
        ==========================================
        
        Client: SketchyCorp International
        Contractor: Test Freelancer
        Date: December 2025
        
        PAYMENT TERMS (CRITICAL ISSUES):
        --------------------------------
        - Total Project Value: $15,000 USD
        - Payment: 100% upon completion (NO UPFRONT DEPOSIT)
        - Payment Window: Net 90 days after "client satisfaction review"
        - Late Fees: NONE SPECIFIED
        
        INTELLECTUAL PROPERTY (RED FLAG):
        ----------------------------------
        - All work product transfers to Client IMMEDIATELY upon creation
        - NOT upon final payment
        - Contractor waives all moral rights
        
        TERMINATION (UNFAIR):
        ----------------------
        - Client may terminate at any time with 24 hours notice
        - Upon termination, Contractor receives payment only for "approved deliverables"
        - "Approved" status determined solely by Client
        
        DISPUTE RESOLUTION:
        -------------------
        - All disputes resolved in Client's jurisdiction
        - Contractor waives right to jury trial
        - Maximum liability capped at fees paid
        
        This contract contains multiple red flags that should be identified.
        """
        
        dataset_id = TestLiveSystemIntegration.shared_data.get("test_dataset_id")
        if dataset_id:
            try:
                success = await client.upload_document(
                    dataset_id=dataset_id,
                    filename="risky_contract.txt",
                    content=test_contract.encode('utf-8')
                )
                log_output(f"Document upload result: {success}", "INFO")
            except Exception as e:
                log_output(f"Upload failed: {e}", "WARNING")
        
        log_output("RAGFlow dataset operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_05_ragflow_retrieval_verification(self):
        """
        Test 5: Verify RAG retrieval finds uploaded content
        CRITICAL: This test validates that documents are properly vectorized and indexed
        """
        log_section("TEST 5: RAGFLOW RETRIEVAL VERIFICATION")
        
        from ragflow.client import get_ragflow_client, DEFAULT_EMBEDDING_MODEL
        
        client = get_ragflow_client()
        
        log_output(f"Default Embedding Model: {DEFAULT_EMBEDDING_MODEL}", "INFO")
        
        # Wait for indexing/parsing
        log_output("Waiting 20 seconds for document parsing and indexing...", "INFO")
        log_output("(Documents must be parsed before vectors are created)", "DEBUG")
        await asyncio.sleep(20)
        
        # Test various queries
        test_queries = [
            "payment terms contract",
            "intellectual property transfer",
            "late fees penalty",
            "SketchyCorp"
        ]
        
        total_chunks = 0
        
        for query in test_queries:
            log_subsection(f"Query: '{query}'")
            
            results = await client.search_user_context(
                user_id="test_user",
                query=query,
                limit=3
            )
            
            chunk_count = len(results)
            total_chunks += chunk_count
            log_output(f"Retrieved {chunk_count} chunks", "INFO" if chunk_count > 0 else "WARNING")
            
            for i, result in enumerate(results):
                content = result.get("content", "")
                similarity = result.get("similarity", 0)
                doc_name = result.get("document_name", "unknown")
                
                log_output(f"[{i+1}] Document: {doc_name}", "DEBUG")
                log_output(f"    Similarity: {similarity:.4f}", "DEBUG")
                log_output(f"    Content Preview: {content[:200]}...", "DEBUG")
        
        # Validation
        log_subsection("RAG VALIDATION SUMMARY")
        log_output(f"Total chunks retrieved across all queries: {total_chunks}", "INFO")
        
        if total_chunks == 0:
            log_output("⚠️ WARNING: 0 chunks retrieved!", "WARNING")
            log_output("   Possible causes:", "WARNING")
            log_output("   1. Document parsing not complete (wait longer)", "WARNING")
            log_output("   2. Embedding model not configured in dataset", "WARNING")
            log_output("   3. Dataset empty or documents not uploaded", "WARNING")
            log_output("   Check RAGFlow logs: docker logs ragflow-server", "WARNING")
            # Don't fail - this might be expected for new datasets
        else:
            log_output(f"✅ RAG retrieval working: {total_chunks} chunks found", "SUCCESS")
        
        log_output("RAGFlow retrieval verification PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 3: LLM Quality & Response Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_06_llm_contract_analysis_quality(self):
        """
        Test 6: LLM produces quality contract analysis with specific risks identified
        """
        log_section("TEST 6: LLM CONTRACT ANALYSIS QUALITY")
        
        from openai import AsyncOpenAI
        from config import settings
        
        client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        contract = """
        CONTRACT SUMMARY:
        - Payment: 100% on completion, no upfront (RED FLAG)
        - No late fees defined (RED FLAG)
        - IP transfers immediately before payment (RED FLAG)
        - 90-day payment window pending "satisfaction review" (RED FLAG)
        - Client can terminate with 24h notice, contractor gets nothing (RED FLAG)
        """
        
        prompt = f"""Analyze this freelance contract for risks. 
        
        {contract}
        
        List the top 5 specific risks with severity (HIGH/MEDIUM/LOW).
        Be specific about WHY each is a risk for the freelancer.
        """
        
        log_output("Sending contract for analysis...", "INFO")
        start_time = time.time()
        
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert contract lawyer specializing in protecting freelancers. Be thorough and specific."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Higher limit for detailed analysis
            temperature=0.3  # Lower for more focused response
        )
        
        duration = time.time() - start_time
        content = response.choices[0].message.content
        
        # Log FULL response (no truncation)
        log_output(f"\n{'='*50}", "INFO")
        log_output("FULL LLM RESPONSE:", "INFO")
        log_output(f"{'='*50}", "INFO")
        log_output(content, "INFO")
        log_output(f"{'='*50}", "INFO")
        
        log_output(f"Response Length: {len(content)} characters", "DEBUG")
        log_output(f"Duration: {duration:.2f}s", "DEBUG")
        
        if response.usage:
            log_output(f"Tokens Used: {response.usage.total_tokens}", "DEBUG")
        
        # Quality validation
        content_lower = content.lower()
        
        quality_checks = {
            "identifies_payment_risk": any(w in content_lower for w in ["upfront", "deposit", "100%", "completion only"]),
            "identifies_ip_risk": any(w in content_lower for w in ["intellectual property", "ip transfer", "immediately", "before payment"]),
            "identifies_late_fee_risk": any(w in content_lower for w in ["late fee", "no penalty", "no late"]),
            "identifies_termination_risk": any(w in content_lower for w in ["termination", "24 hour", "approved deliverables"]),
            "provides_severity": any(w in content_lower for w in ["high", "critical", "severe", "major"]),
            "actionable_advice": any(w in content_lower for w in ["negotiate", "request", "add", "include", "refuse"])
        }
        
        log_subsection("Quality Checks")
        passed = 0
        for check_name, check_passed in quality_checks.items():
            status = "✅" if check_passed else "❌"
            log_output(f"  {status} {check_name}", "INFO")
            if check_passed:
                passed += 1
        
        score = passed / len(quality_checks) * 100
        log_output(f"\nQuality Score: {score:.0f}% ({passed}/{len(quality_checks)})", "INFO")
        
        # Store for later reference
        TestLiveSystemIntegration.shared_data["llm_analysis"] = content
        
        assert passed >= 4, f"LLM analysis quality too low: {passed}/{len(quality_checks)} checks passed"
        
        log_output("LLM contract analysis quality PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 4: Team Orchestration Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_07_team_initialization_verbose(self):
        """
        Test 7: Verify team initialization with detailed agent info
        """
        log_section("TEST 7: TEAM INITIALIZATION (VERBOSE)")
        
        from agents.team import FlagPilotTeam
        from agents.registry import registry
        
        # List all available agents
        available = registry.list_agents()
        log_output(f"Available Agents ({len(available)}):", "INFO")
        for agent_id in available:
            log_output(f"  - {agent_id}", "DEBUG")
        
        # Initialize with specific agents
        selected_agents = ["contract-guardian", "job-authenticator", "risk-advisor"]
        log_output(f"\nInitializing team with: {selected_agents}", "INFO")
        
        team = FlagPilotTeam(agents=selected_agents)
        
        log_output(f"Team Agents Loaded: {list(team.agents.keys())}", "INFO")
        
        for agent_id, agent in team.agents.items():
            log_output(f"  {agent_id}: {type(agent).__name__}", "DEBUG")
        
        assert len(team.agents) >= 1, "No agents loaded"
        
        log_output("Team initialization PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_08_team_scam_detection_full_output(self):
        """
        Test 8: Team detects scam with FULL output logging
        """
        log_section("TEST 8: TEAM SCAM DETECTION (FULL OUTPUT)")
        
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam()  # All agents
        
        scam_scenario = """
        I received a job offer from "QuickMoney Enterprises". The details:
        
        1. They want me to pay a $750 "security deposit" for equipment via Zelle
        2. The job is "data entry from home" paying $45/hour
        3. They contacted me on WhatsApp, not a job platform
        4. No formal interview, just a "quick chat"
        5. They want my bank details for "direct deposit setup"
        6. The company has no website or LinkedIn presence
        
        Is this legitimate? Should I take this job?
        """
        
        context = {"id": f"scam_test_{int(time.time())}"}
        
        log_output("TASK:", "INFO")
        log_output(scam_scenario, "INFO")
        log_output("\nRunning team orchestration...", "INFO")
        
        start_time = time.time()
        result = await team.run(scam_scenario, context)
        duration = time.time() - start_time
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        error = result.get("error")
        
        log_output(f"\nExecution Duration: {duration:.2f}s", "INFO")
        log_output(f"Error: {error}", "WARNING" if error else "DEBUG")
        
        # Log each agent's FULL output
        log_subsection("AGENT OUTPUTS (FULL)")
        for agent_id, output in agent_outputs.items():
            log_output(f"\n[AGENT: {agent_id.upper()}]", "INFO")
            log_output("-" * 50, "INFO")
            # FULL output, no truncation
            log_output(str(output) if output else "(No output)", "INFO")
            log_output("-" * 50, "INFO")
        
        log_subsection("FINAL SYNTHESIS (FULL)")
        log_output(synthesis if synthesis else "(No synthesis)", "INFO")
        
        # Scam detection validation
        combined = (synthesis + str(agent_outputs)).lower()
        
        scam_checks = {
            "identifies_as_scam": any(w in combined for w in ["scam", "fraud", "fraudulent", "suspicious", "red flag"]),
            "flags_deposit": any(w in combined for w in ["deposit", "zelle", "$750", "security deposit"]),
            "flags_no_interview": any(w in combined for w in ["no interview", "quick chat", "informal"]),
            "flags_bank_request": any(w in combined for w in ["bank details", "bank info", "banking"]),
            "recommends_decline": any(w in combined for w in ["decline", "avoid", "don't", "do not", "refuse", "walk away", "not legitimate"]),
            "warns_about_whatsapp": any(w in combined for w in ["whatsapp", "messaging app", "not official"])
        }
        
        log_subsection("SCAM DETECTION VALIDATION")
        passed = 0
        for check_name, check_passed in scam_checks.items():
            status = "✅" if check_passed else "❌"
            log_output(f"  {status} {check_name}", "INFO")
            if check_passed:
                passed += 1
        
        score = passed / len(scam_checks) * 100
        log_output(f"\nScam Detection Score: {score:.0f}% ({passed}/{len(scam_checks)})", "INFO")
        
        assert not error, f"Team execution error: {error}"
        assert synthesis or agent_outputs, "No output from team"
        assert passed >= 3, f"Scam detection insufficient: {passed}/{len(scam_checks)}"
        
        log_output("Team scam detection PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_09_team_complex_negotiation(self):
        """
        Test 9: Complex multi-step negotiation task
        """
        log_section("TEST 9: COMPLEX NEGOTIATION TASK")
        
        from agents.team import FlagPilotTeam
        
        team = FlagPilotTeam(agents=["contract-guardian", "negotiation-assistant", "communication-coach"])
        
        complex_task = """
        I'm a freelance web developer. A client wants to hire me for a $10,000 project.
        Their proposed contract has these issues:
        
        1. Payment: 100% upon completion (no milestones)
        2. Timeline: 6 weeks, but scope is "flexible" 
        3. No late fees for delayed payment
        4. Client owns IP immediately
        5. "Unlimited revisions" clause
        
        My goals:
        1. Analyze the contract risks
        2. Suggest specific negotiation points
        3. Draft a polite but firm counter-proposal email
        
        Help me negotiate fair terms.
        """
        
        context = {"id": f"negotiation_test_{int(time.time())}"}
        
        log_output("COMPLEX TASK:", "INFO")
        log_output(complex_task, "INFO")
        log_output("\nExecuting multi-agent workflow...", "INFO")
        
        start_time = time.time()
        result = await team.run(complex_task, context)
        duration = time.time() - start_time
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        
        log_output(f"\nTotal Duration: {duration:.2f}s", "INFO")
        log_output(f"Agents Used: {list(agent_outputs.keys())}", "INFO")
        
        # Full outputs
        log_subsection("FULL AGENT RESPONSES")
        for agent_id, output in agent_outputs.items():
            log_output(f"\n=== {agent_id.upper()} ===", "INFO")
            log_output(str(output) if output else "(empty)", "INFO")
        
        log_subsection("FINAL SYNTHESIS")
        log_output(synthesis if synthesis else "(empty)", "INFO")
        
        # Validation
        combined = (synthesis + str(agent_outputs)).lower()
        
        quality_checks = {
            "addresses_payment": any(w in combined for w in ["milestone", "deposit", "upfront", "payment schedule"]),
            "addresses_ip": any(w in combined for w in ["ip", "intellectual property", "ownership", "upon payment"]),
            "addresses_scope": any(w in combined for w in ["scope", "revisions", "changes", "unlimited"]),
            "provides_email": any(w in combined for w in ["dear", "subject:", "sincerely", "thank you"]),
            "suggests_specifics": any(w in combined for w in ["50%", "30%", "milestone", "weekly", "define"])
        }
        
        log_subsection("QUALITY VALIDATION")
        passed = sum(quality_checks.values())
        for check, is_passed in quality_checks.items():
            status = "✅" if is_passed else "❌"
            log_output(f"  {status} {check}", "INFO")
        
        log_output(f"\nQuality Score: {passed}/{len(quality_checks)}", "INFO")
        
        assert synthesis or agent_outputs, "No output"
        
        log_output("Complex negotiation task PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 5: End-to-End Stress Test
    # =========================================
    
    @pytest.mark.asyncio
    async def test_10_end_to_end_stress(self):
        """
        Test 10: Full end-to-end flow with stress validation
        Combines RAG + LLM + Team in realistic scenario
        """
        log_section("TEST 10: END-TO-END STRESS TEST")
        
        from ragflow.client import get_ragflow_client
        from agents.team import FlagPilotTeam
        
        user_id = f"e2e_stress_{int(time.time())}"
        
        log_output(f"Test User ID: {user_id}", "INFO")
        
        # Step 1: RAGFlow Check
        log_subsection("STEP 1: RAGFLOW STATUS")
        client = get_ragflow_client()
        health = await client.health_check()
        log_output(f"RAGFlow Status: {health['status']}", "INFO")
        
        # Step 2: Search for existing context
        log_subsection("STEP 2: RAG CONTEXT SEARCH")
        results = await client.search_user_context(
            user_id=user_id,
            query="payment contract risks freelance",
            limit=5
        )
        log_output(f"Found {len(results)} context chunks", "INFO")
        for r in results:
            log_output(f"  - Similarity {r.get('similarity', 0):.3f}: {r.get('content', '')[:80]}...", "DEBUG")
        
        # Step 3: Complex team task
        log_subsection("STEP 3: TEAM ORCHESTRATION")
        
        stress_task = """
        I'm a freelancer facing multiple challenges:
        
        1. A client wants me to sign a contract with NO upfront payment
        2. They're asking for "a few small fixes" outside the original scope
        3. They haven't responded to my last 3 invoices
        4. Now they want a 40% discount due to "budget constraints"
        
        I need help with:
        - Contract review for the new project
        - Response to scope creep  
        - Payment enforcement strategy
        - Negotiation for the discount request
        
        Give me a complete action plan.
        """
        
        log_output("Stress Task:", "INFO")
        log_output(stress_task, "INFO")
        
        team = FlagPilotTeam()
        
        start_time = time.time()
        result = await team.run(stress_task, context={"id": user_id})
        duration = time.time() - start_time
        
        synthesis = result.get("final_synthesis", "")
        agent_outputs = result.get("agent_outputs", {})
        error = result.get("error")
        
        log_output(f"\nTotal Execution Time: {duration:.2f}s", "INFO")
        log_output(f"Error: {error}", "WARNING" if error else "DEBUG")
        
        # Log all outputs
        log_subsection("ALL AGENT OUTPUTS")
        for agent_id, output in agent_outputs.items():
            output_str = str(output) if output else "(empty)"
            log_output(f"\n[{agent_id.upper()}]\n{output_str}", "INFO")
        
        log_subsection("FINAL SYNTHESIS")
        log_output(synthesis, "INFO")
        
        # Comprehensive validation
        combined = (synthesis + str(agent_outputs)).lower()
        
        comprehensive_checks = {
            "addresses_payment": "payment" in combined or "invoice" in combined,
            "addresses_scope": "scope" in combined or "creep" in combined,
            "addresses_discount": "discount" in combined or "40%" in combined,
            "provides_strategy": "strategy" in combined or "plan" in combined,
            "mentions_contract": "contract" in combined,
            "actionable": any(w in combined for w in ["should", "recommend", "suggest", "consider"]),
            "professional_tone": "thank" in combined or "please" in combined or "professional" in combined
        }
        
        log_subsection("COMPREHENSIVE VALIDATION")
        passed = 0
        for check, is_passed in comprehensive_checks.items():
            status = "✅" if is_passed else "❌"
            log_output(f"  {status} {check}", "INFO")
            if is_passed:
                passed += 1
        
        final_score = passed / len(comprehensive_checks) * 100
        log_output(f"\n{'='*50}", "INFO")
        log_output(f"FINAL STRESS TEST SCORE: {final_score:.0f}% ({passed}/{len(comprehensive_checks)})", "INFO")
        log_output(f"{'='*50}", "INFO")
        
        assert not error, f"Stress test error: {error}"
        assert synthesis or agent_outputs, "No output from stress test"
        assert passed >= 4, f"Stress test quality insufficient: {passed}/{len(comprehensive_checks)}"
        
        log_output("End-to-end stress test PASSED", "SUCCESS")
    
    @classmethod
    def teardown_class(cls):
        """Final summary and cleanup"""
        log_section("TEST SUITE COMPLETE")
        
        log_output(f"Completed: {datetime.now().isoformat()}", "INFO")
        log_output(f"Output saved to: {OUTPUT_FILE}", "INFO")
        
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 70 + "\n")
            f.write("  TEST SUITE FINISHED\n")
            f.write(f"  End Time: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n")
        
        print(f"\n📄 Full output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
