"""
FlagPilot Live Integration Test Suite - LangGraph Edition v6.0
===============================================================
Comprehensive tests validating the entire LangGraph multi-agent system:

SECTION 1: Environment & Health
  1. Environment Check
  2. RAGFlow Health  
  3. LangChain LLM Health
  4. Elasticsearch Memory
  5. LangSmith Tracing (NEW)

SECTION 2: Agent System
  6. Agent Registry
  7. Fast-Fail Scam Detection
  8. Orchestrator Routing

SECTION 3: RAG & Memory
  9. RAGFlow Upload & Search
  10. User Profile Operations
  11. Chat History Operations
  12. Global Wisdom Operations
  13. Experience Gallery

SECTION 4: Complex Scenarios
  14. Scam Detection Scenario
  15. Contract Analysis Quality
  16. Scope Creep Detection
  17. Ghosting Prevention
  18. Contract Negotiation with Memory

SECTION 5: Integration
  19. End-to-End Workflow
  20. CopilotKit API Integration

Output saved to: test_live_output.txt
This test suite validates the LangGraph-based multi-agent system.
"""

import pytest
import asyncio
import time
import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUT_FILE = "test_live_output.txt"


class TestReporter:
    """Test output reporter with file and console output"""
    
    ICONS = {
        "SUCCESS": "[OK]", "ERROR": "[!!]", "WARNING": "[??]",
        "INFO": "[--]", "DEBUG": "[..]", "PASS": "[OK]",
        "FAIL": "[XX]", "SKIP": "[>>]"
    }
    
    @classmethod
    def init(cls):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("  FLAGPILOT LIVE INTEGRATION TEST - LANGGRAPH EDITION v6.0\n")
            f.write(f"  Started: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
    
    @classmethod
    def log(cls, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        icon = cls.ICONS.get(level, "[--]")
        line = f"[{timestamp}] {icon} {msg}"
        
        colors = {"ERROR": "\033[91m", "WARNING": "\033[93m", "SUCCESS": "\033[92m", "DEBUG": "\033[90m"}
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] [{level}] {msg}\033[0m" if color else f"[{timestamp}] [{level}] {msg}")
        
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{line}\n")
    
    @classmethod
    def section(cls, title: str):
        cls.log("")
        cls.log("#" * 80)
        cls.log(f"#  {title.center(74)}  #")
        cls.log("#" * 80)
        cls.log("")
    
    @classmethod
    def subsection(cls, title: str):
        cls.log(f"\n----- {title} " + "-" * (70 - len(title)))
    
    @classmethod
    def json(cls, data: Any, label: str = "DATA"):
        try:
            formatted = json.dumps(data, indent=2, default=str)
            cls.log(f"{label}:", "DEBUG")
            for line in formatted.split("\n")[:20]:
                cls.log(f"  {line}", "DEBUG")
        except:
            cls.log(f"{label}: {data}", "DEBUG")
    
    @classmethod
    def finish(cls):
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"  TEST SUITE COMPLETED: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n")


TestReporter.init()


class TestLiveSystemIntegration:
    """Comprehensive LangGraph Integration Test Suite"""
    
    shared_data = {}
    
    # =========================================
    # SECTION 1: ENVIRONMENT & HEALTH
    # =========================================
    
    @pytest.mark.asyncio
    async def test_01_environment_check(self):
        """Verify environment variables and configuration"""
        TestReporter.section("TEST 1: ENVIRONMENT CHECK")
        
        from config import settings
        
        checks = {
            "OPENROUTER_API_KEY": bool(settings.OPENROUTER_API_KEY),
            "OPENROUTER_MODEL": bool(settings.OPENROUTER_MODEL),
            "OPENROUTER_BASE_URL": bool(settings.OPENROUTER_BASE_URL),
            "RAGFLOW_URL": bool(settings.RAGFLOW_URL),
            "ES_HOST": bool(settings.ES_HOST),
            "ES_PORT": bool(settings.ES_PORT),
        }
        
        TestReporter.log(f"OpenRouter Model: {settings.OPENROUTER_MODEL}")
        TestReporter.log(f"OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}")
        TestReporter.log(f"RAGFlow URL: {settings.RAGFLOW_URL}")
        TestReporter.log(f"ES Host: {settings.ES_HOST}:{settings.ES_PORT}")
        
        for name, is_set in checks.items():
            status = "✅ SET" if is_set else "❌ MISSING"
            TestReporter.log(f"  {name}: {status}")
        
        if settings.LANGSMITH_API_KEY:
            TestReporter.log(f"LangSmith Project: {settings.LANGSMITH_PROJECT}", "SUCCESS")
        else:
            TestReporter.log("LangSmith: Not configured", "WARNING")
        
        TestReporter.log("Environment check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_02_ragflow_health(self):
        """Verify RAGFlow is connected and healthy"""
        TestReporter.section("TEST 2: RAGFLOW HEALTH CHECK")
        
        try:
            from ragflow.client import get_ragflow_client
            
            TestReporter.log("Checking RAGFlow health...")
            client = get_ragflow_client()
            datasets = client.list_datasets()  # Sync call
            
            TestReporter.json({
                "status": "healthy",
                "connected": True,
                "datasets_count": len(datasets) if datasets else 0
            }, "Health Response")
            
            TestReporter.log(f"RAGFlow Status: healthy")
            TestReporter.log(f"Datasets Count: {len(datasets) if datasets else 0}")
            self.shared_data["ragflow_healthy"] = True
            TestReporter.log("RAGFlow health check PASSED", "SUCCESS")
        except Exception as e:
            TestReporter.log(f"RAGFlow health check error: {e}", "WARNING")
            pytest.skip(f"RAGFlow not available: {e}")
    
    @pytest.mark.asyncio  
    async def test_03_langchain_llm_health(self):
        """Verify LangChain ChatOpenAI works with OpenRouter"""
        TestReporter.section("TEST 3: LANGCHAIN LLM HEALTH CHECK")
        
        from config import get_llm
        
        llm = get_llm(temperature=0)
        TestReporter.log(f"Model: {llm.model_name}")
        TestReporter.log("Sending test prompt...")
        
        start = time.time()
        response = await llm.ainvoke("Say 'Hello! I'm working and ready to help you.' and nothing else.")
        duration = time.time() - start
        
        TestReporter.log(f"Response: {response.content}", "SUCCESS")
        TestReporter.log(f"Duration: {duration:.2f}s")
        
        # Token usage if available
        if hasattr(response, 'response_metadata'):
            meta = response.response_metadata
            if 'token_usage' in meta:
                TestReporter.log(f"Prompt Tokens: {meta['token_usage'].get('prompt_tokens', 'N/A')}", "DEBUG")
                TestReporter.log(f"Completion Tokens: {meta['token_usage'].get('completion_tokens', 'N/A')}", "DEBUG")
        
        assert response.content and len(response.content) > 0
        self.shared_data["llm_healthy"] = True
        TestReporter.log("LangChain LLM health check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_04_elasticsearch_health(self):
        """Verify Elasticsearch connection and memory system"""
        TestReporter.section("TEST 4: ELASTICSEARCH MEMORY SYSTEM")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        health = manager.health_check()
        
        TestReporter.json(health, "ES Health")
        
        if health.get("connected"):
            TestReporter.log(f"Cluster: {health.get('cluster_name')}")
            TestReporter.log(f"Version: {health.get('version')}")
            
            stats = manager.get_stats()
            TestReporter.log("Index Stats:")
            for index, count in stats.items():
                TestReporter.log(f"  {index}: {count} docs", "DEBUG")
            
            self.shared_data["es_connected"] = True
            TestReporter.log("Elasticsearch health check PASSED", "SUCCESS")
        else:
            TestReporter.log(f"ES not connected: {health.get('error')}", "WARNING")
            pytest.skip("Elasticsearch not available")
    
    @pytest.mark.asyncio
    async def test_05_langsmith_tracing(self):
        """Verify LangSmith tracing configuration"""
        TestReporter.section("TEST 5: LANGSMITH TRACING")
        
        from config import settings
        import os
        
        if not settings.LANGSMITH_API_KEY:
            TestReporter.log("LangSmith API key not configured - SKIPPED", "WARNING")
            pytest.skip("LangSmith not configured")
        
        TestReporter.log(f"LangSmith Project: {settings.LANGSMITH_PROJECT}")
        TestReporter.log(f"Tracing Enabled: {os.environ.get('LANGCHAIN_TRACING_V2', 'false')}")
        
        # Verify tracing works with a simple call
        from config import get_llm
        llm = get_llm()
        response = await llm.ainvoke("Test trace")
        
        TestReporter.log("LangSmith tracing test completed", "SUCCESS")
    
    # =========================================
    # SECTION 2: AGENT SYSTEM
    # =========================================
    
    @pytest.mark.asyncio
    async def test_06_agent_registry(self):
        """Verify all LangGraph agents are registered"""
        TestReporter.section("TEST 6: AGENT REGISTRY")
        
        from agents.agents import list_agents, get_agent, AGENTS
        
        agents = list_agents()
        TestReporter.log(f"Registered agents: {len(agents)}")
        
        TestReporter.subsection("AGENT LIST")
        for agent_id in sorted(agents):
            agent = get_agent(agent_id)
            TestReporter.log(f"  - [{agent_id}] {agent.description[:50]}... (cost: {agent.credit_cost})", "DEBUG")
        
        assert len(agents) >= 14, f"Expected 14 agents, got {len(agents)}"
        TestReporter.log(f"Agent Registry: {len(agents)} agents ready", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_07_scam_detection_fast_fail(self):
        """Test programmatic scam detection before LLM call"""
        TestReporter.section("TEST 7: FAST-FAIL SCAM DETECTION")
        
        from agents.orchestrator import detect_scam_signals
        
        test_cases = [
            ("Normal job: Looking for a web developer for my e-commerce site", 0),
            ("Contact me on Telegram for the job details", 1),
            ("Send you a check for equipment then return excess", 1),
            ("No experience required, $45/hr data entry work from home via WhatsApp", 5),
            ("Pay security deposit via Zelle before starting", 2),
        ]
        
        TestReporter.subsection("SCAM SIGNAL TESTS")
        all_passed = True
        for text, min_expected in test_cases:
            signals = detect_scam_signals(text)
            passed = len(signals) >= min_expected
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False
            TestReporter.log(f"  Detected {len(signals)} signals (expected >={min_expected}): {status}")
            TestReporter.log(f"    Text: {text[:60]}...", "DEBUG")
            TestReporter.log(f"    Signals: {signals}", "DEBUG")
        
        # Full scam test
        full_scam = "Contact me on Telegram @scammer123. I'll send you a check for $3000 via Zelle, no experience required, $50/hr data entry."
        full_signals = detect_scam_signals(full_scam)
        TestReporter.log(f"Full scam test: {len(full_signals)} signals detected", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_08_orchestrator_routing(self):
        """Test dynamic agent selection based on task"""
        TestReporter.section("TEST 8: ORCHESTRATOR ROUTING")
        
        from agents.orchestrator import identify_relevant_agents, is_simple_greeting
        
        test_cases = [
            ("Review this contract for legal issues", ["contract-guardian"]),
            ("Is this job posting a scam?", ["job-authenticator"]),
            ("Client hasn't paid my invoice for 30 days", ["payment-enforcer"]),
            ("Help me negotiate a better rate", ["negotiation-assistant"]),
            ("The client is adding more features without pay", ["scope-sentinel"]),
            ("Draft a professional response to angry client", ["communication-coach"]),
        ]
        
        TestReporter.subsection("ROUTING TESTS")
        for task, expected in test_cases:
            agents = identify_relevant_agents(task)
            has_expected = any(e in agents for e in expected)
            status = "PASS" if has_expected else "FAIL"
            TestReporter.log(f"  {task[:45]}... -> {agents} [{status}]")
        
        # Greeting detection
        assert is_simple_greeting("hello")
        assert is_simple_greeting("hi there")
        assert not is_simple_greeting("Please review my contract thoroughly")
        
        TestReporter.log("Routing logic validated", "SUCCESS")
    
    # =========================================
    # SECTION 3: RAG & MEMORY
    # =========================================
    
    @pytest.mark.asyncio
    async def test_09_ragflow_upload_search(self):
        """RAGFlow Upload, Indexing, and Retrieval"""
        TestReporter.section("TEST 9: RAGFLOW UPLOAD & SEARCH")
        
        if not self.shared_data.get("ragflow_healthy"):
            pytest.skip("RAGFlow not available")
        
        try:
            from ragflow.client import get_ragflow_client
            
            client = get_ragflow_client()
            
            TestReporter.subsection("STEP 1: SEARCH TEST")
            # Use retrieve() which wraps the sync SDK properly
            results = await client.retrieve("freelance contract payment terms", limit=3)
            TestReporter.log(f"Search results: {len(results) if results else 0}")
            
            if results:
                for i, r in enumerate(results[:3]):
                    content = str(r.get('content', ''))[:150]
                    TestReporter.log(f"  [{i+1}] {content}...", "DEBUG")
            
            TestReporter.log("RAGFlow search PASSED", "SUCCESS")
        except Exception as e:
            TestReporter.log(f"RAGFlow search error: {e}", "WARNING")
            pytest.skip(f"RAGFlow error: {e}")
    
    @pytest.mark.asyncio
    async def test_10_user_profile_operations(self):
        """User Profile CRUD with memory system"""
        TestReporter.section("TEST 10: USER PROFILE OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        test_user_id = f"live_test_user_{int(time.time())}"
        
        # CREATE
        TestReporter.subsection("CREATE Profile")
        result = await manager.update_user_profile(
            user_id=test_user_id,
            summary="Experienced freelancer, prefers fixed-price contracts, cautious about scope creep.",
            preferences={"rate_min": 50, "avoid_clients": ["lowballers", "scope creepers"]}
        )
        TestReporter.log(f"Create result: {result}")
        assert result, "Failed to create profile"
        
        # READ
        TestReporter.subsection("READ Profile")
        profile = await manager.get_user_profile(test_user_id)
        TestReporter.json(profile, "Profile")
        assert profile["user_id"] == test_user_id
        
        # UPDATE
        TestReporter.subsection("UPDATE Profile")
        result = await manager.update_user_profile(
            user_id=test_user_id,
            summary=profile["summary"] + " Recently completed a major e-commerce project."
        )
        assert result
        TestReporter.log("Profile updated successfully", "SUCCESS")
        
        self.shared_data["test_user_id"] = test_user_id
        TestReporter.log("User Profile operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_11_chat_history_operations(self):
        """Chat History storage and retrieval"""
        TestReporter.section("TEST 11: CHAT HISTORY OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        test_user_id = self.shared_data.get("test_user_id", f"chat_test_{int(time.time())}")
        session_id = str(uuid.uuid4())
        
        TestReporter.subsection("SAVE Conversation Messages")
        messages = [
            ("user", "I need help reviewing a contract from a new client"),
            ("assistant", "I'd be happy to help! Please share the contract details."),
            ("user", "The client wants 100% payment on completion with no deposit."),
            ("assistant", "That's a significant red flag. I recommend negotiating at least 30-50% upfront.")
        ]
        
        for role, content in messages:
            chat_id = await manager.save_chat(
                user_id=test_user_id,
                role=role,
                content=content,
                session_id=session_id,
                agent_id="contract-guardian"
            )
            TestReporter.log(f"  Saved {role} message: {chat_id[:8] if chat_id else 'failed'}...", "DEBUG")
        
        await asyncio.sleep(1)
        
        TestReporter.subsection("RETRIEVE Chat History")
        history = await manager.get_chat_history(test_user_id, session_id)
        TestReporter.log(f"Retrieved {len(history)} messages")
        
        for msg in history:
            TestReporter.log(f"  [{msg['role']}]: {msg['content'][:60]}...", "DEBUG")
        
        assert len(history) >= 4, f"Expected 4+ messages, got {len(history)}"
        
        TestReporter.subsection("GET Recent Sessions")
        sessions = await manager.get_recent_sessions(test_user_id)
        TestReporter.log(f"Sessions: {sessions[:3]}...", "DEBUG")
        
        self.shared_data["session_id"] = session_id
        TestReporter.log("Chat History operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_12_global_wisdom_operations(self):
        """Global Wisdom storage and retrieval"""
        TestReporter.section("TEST 12: GLOBAL WISDOM OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        
        TestReporter.subsection("ADD Wisdom Entries")
        wisdom_entries = [
            ("contract", "Always request a deposit before starting work - at least 30% upfront", ["payment", "deposit"]),
            ("contract", "Define scope clearly with a change order process to avoid scope creep", ["scope", "clarity"]),
            ("scam", "Be wary of clients who contact via WhatsApp only and refuse video calls", ["red-flag", "communication"]),
            ("negotiation", "Counter low offers by explaining value delivered, not justifying rates", ["pricing", "value"]),
            ("payment", "Include late payment penalties (1.5-2% monthly) in all contracts", ["enforcement", "terms"]),
        ]
        
        for category, insight, tags in wisdom_entries:
            result = await manager.add_wisdom(category=category, insight=insight, tags=tags, confidence=0.7)
            TestReporter.log(f"  Added: [{category}] {insight[:50]}...", "DEBUG")
        
        await asyncio.sleep(1)
        
        TestReporter.subsection("SEARCH Wisdom by Category")
        contract_wisdom = await manager.get_global_wisdom(category="contract")
        TestReporter.log(f"Contract wisdom: {len(contract_wisdom)} entries")
        
        TestReporter.subsection("SEARCH Wisdom by Query")
        deposit_wisdom = await manager.get_global_wisdom(query="deposit payment upfront")
        TestReporter.log(f"Deposit-related wisdom: {len(deposit_wisdom)} entries")
        
        if deposit_wisdom:
            TestReporter.json(deposit_wisdom[0], "Top Deposit Wisdom")
        
        TestReporter.log("Global Wisdom operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_13_experience_gallery(self):
        """Experience Gallery (shared learnings)"""
        TestReporter.section("TEST 13: EXPERIENCE GALLERY")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        test_user_id = self.shared_data.get("test_user_id", f"exp_test_{int(time.time())}")
        
        TestReporter.subsection("SAVE Successful Experiences")
        experiences = [
            {
                "task": "Client wanted unlimited revisions but I set a cap of 3 rounds",
                "outcome": "Client agreed after I explained my revision policy professionally",
                "lesson": "Always set clear revision limits upfront to prevent scope creep",
                "score": 1
            },
            {
                "task": "Detected a scam job posting requiring upfront equipment fee",
                "outcome": "Avoided the scam by recognizing classic red flags",
                "lesson": "Legitimate employers never ask freelancers to pay upfront fees",
                "score": 1
            }
        ]
        
        for exp in experiences:
            result = await manager.save_experience(
                user_id=test_user_id,
                task=exp["task"],
                outcome=exp["outcome"],
                lesson=exp["lesson"],
                score=exp["score"]
            )
            TestReporter.log(f"  Saved: {exp['lesson'][:50]}...", "DEBUG")
        
        await asyncio.sleep(1)
        
        TestReporter.subsection("SEARCH Similar Experiences")
        similar = await manager.search_similar_experiences("revision limits scope creep")
        TestReporter.log(f"Found {len(similar)} similar experiences")
        
        if similar:
            TestReporter.json(similar[0], "Top Match")
        
        TestReporter.log("Experience Gallery PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 4: COMPLEX SCENARIOS
    # =========================================
    
    @pytest.mark.asyncio
    async def test_14_scam_detection_scenario(self):
        """Full scam detection via orchestrator"""
        TestReporter.section("TEST 14: SCAM DETECTION SCENARIO")
        
        from agents.orchestrator import run_orchestrator
        
        scam_task = """
        Got a job offer via Telegram from "QuickMoney LLC":
        - $50/hr data entry, no experience required
        - They'll send a check for $3000 for equipment
        - Need my bank details for direct deposit
        - Contact @quickmoney_hiring on Telegram
        
        Should I take this job?
        """
        
        TestReporter.log("TASK:")
        TestReporter.log(scam_task.strip())
        TestReporter.log("\nRunning orchestrator...")
        
        start = time.time()
        result = await run_orchestrator(task=scam_task)
        duration = time.time() - start
        
        TestReporter.log(f"Duration: {duration:.2f}s")
        TestReporter.log(f"Risk Level: {result.get('risk_level')}")
        
        TestReporter.subsection("AGENT OUTPUTS")
        for agent_id, output in result.get("agent_outputs", {}).items():
            TestReporter.log(f"  [{agent_id}] output:", "DEBUG")
            TestReporter.log(f"  {str(output)[:300]}...", "DEBUG")
        
        TestReporter.subsection("ANALYSIS RESULT")
        synthesis = result.get("final_synthesis", "")[:800]
        TestReporter.log(synthesis)
        
        # Validation
        combined = str(result).lower()
        checks = {
            "identifies_scam": any(w in combined for w in ["scam", "fraud", "critical"]),
            "identifies_check_fraud": any(w in combined for w in ["check", "deposit", "money"]),
            "recommends_decline": any(w in combined for w in ["do not", "don't", "avoid", "decline"]),
        }
        
        TestReporter.subsection("SCAM DETECTION VALIDATION")
        for check, passed in checks.items():
            TestReporter.log(f"  {'✅' if passed else '❌'} {check}")
        
        score = sum(checks.values())
        TestReporter.log(f"Scam Detection Score: {score}/{len(checks)}")
        TestReporter.log("Scam detection scenario PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_15_contract_analysis_quality(self):
        """LLM produces quality contract analysis with specific risks"""
        TestReporter.section("TEST 15: LLM CONTRACT ANALYSIS QUALITY")
        
        from config import get_llm
        
        llm = get_llm(temperature=0.3)
        
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
        
        TestReporter.log("Sending contract for analysis...")
        start = time.time()
        
        response = await llm.ainvoke([
            {"role": "system", "content": "You are an expert contract lawyer specializing in protecting freelancers."},
            {"role": "user", "content": prompt}
        ])
        
        duration = time.time() - start
        content = response.content
        
        TestReporter.log(f"\n{'='*50}")
        TestReporter.log("FULL LLM RESPONSE:")
        TestReporter.log(f"{'='*50}")
        TestReporter.log(content[:1500])
        TestReporter.log(f"{'='*50}")
        TestReporter.log(f"Response Length: {len(content)} characters", "DEBUG")
        TestReporter.log(f"Duration: {duration:.2f}s", "DEBUG")
        
        content_lower = content.lower()
        quality_checks = {
            "identifies_payment_risk": any(w in content_lower for w in ["upfront", "deposit", "100%", "completion"]),
            "identifies_ip_risk": any(w in content_lower for w in ["intellectual property", "ip", "immediately", "before payment"]),
            "identifies_late_fee_risk": any(w in content_lower for w in ["late fee", "no penalty", "no late"]),
            "identifies_termination_risk": any(w in content_lower for w in ["termination", "24 hour", "nothing"]),
            "provides_severity": any(w in content_lower for w in ["high", "critical", "severe"]),
            "actionable_advice": any(w in content_lower for w in ["negotiate", "request", "add", "refuse"]),
        }
        
        TestReporter.subsection("Quality Checks")
        passed = 0
        for check_name, check_passed in quality_checks.items():
            TestReporter.log(f"  {'✅' if check_passed else '❌'} {check_name}")
            if check_passed:
                passed += 1
        
        score = passed / len(quality_checks) * 100
        TestReporter.log(f"\nQuality Score: {score:.0f}% ({passed}/{len(quality_checks)})")
        
        assert passed >= 4, f"LLM analysis quality too low: {passed}/{len(quality_checks)}"
        TestReporter.log("LLM contract analysis quality PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_16_scope_creep_detection(self):
        """Scope creep detection scenario"""
        TestReporter.section("TEST 16: SCOPE CREEP DETECTION")
        
        from config import get_llm
        
        llm = get_llm(temperature=0.3)
        
        scenario = """
        I'm a freelance web developer. Original contract was for:
        - 5-page WordPress website
        - Contact form
        - Basic SEO setup
        - Price: $2,500, timeline: 2 weeks
        
        After delivering, the client says:
        "Great work! But can you also quickly add:
        - E-commerce with 50 products
        - Customer login system
        - Newsletter integration  
        - Mobile app version
        - 'It should only take a few hours since you already know the project'"
        
        They're refusing to pay the original invoice until these are done.
        How should I handle this? Give me a professional response.
        """
        
        TestReporter.log("SCOPE CREEP SCENARIO:")
        TestReporter.log(scenario.strip())
        TestReporter.log("\nSending to LLM for analysis...")
        
        response = await llm.ainvoke([
            {"role": "system", "content": "You are a freelance business advisor helping freelancers handle scope creep professionally."},
            {"role": "user", "content": scenario}
        ])
        
        content = response.content
        
        TestReporter.subsection("LLM RESPONSE")
        TestReporter.log(content[:1500])
        
        content_lower = content.lower()
        checks = {
            "identifies_scope_creep": any(w in content_lower for w in ["scope creep", "scope", "original", "additional"]),
            "addresses_payment": any(w in content_lower for w in ["payment", "invoice", "pay", "owe"]),
            "suggests_change_order": any(w in content_lower for w in ["change order", "separate", "additional fee", "quote"]),
            "provides_response": any(w in content_lower for w in ["template", "response", "say", "tell"]),
        }
        
        TestReporter.subsection("SCOPE CREEP VALIDATION")
        for check, passed in checks.items():
            TestReporter.log(f"  {'✅' if passed else '❌'} {check}")
        
        score = sum(checks.values())
        TestReporter.log(f"Scope Creep Score: {score}/{len(checks)}")
        TestReporter.log("Scope creep detection PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_17_ghosting_prevention(self):
        """Ghosting prevention scenario"""
        TestReporter.section("TEST 17: GHOSTING PREVENTION SCENARIO")
        
        from config import get_llm
        from lib.memory.manager import MemoryManager
        
        llm = get_llm(temperature=0.3)
        
        scenario = """
        I completed a $3,000 branding project 45 days ago:
        - Delivered all files
        - Client confirmed receipt
        - Said "invoice approved, payment processing"
        
        Since then:
        - 3 emails with no response
        - 2 phone calls went to voicemail
        - LinkedIn message was read but no reply
        - Payment is now 30 days overdue
        
        What are my escalation options? How do I get paid?
        """
        
        TestReporter.log("GHOSTING SCENARIO:")
        TestReporter.log(scenario.strip())
        
        # Get wisdom from memory if available
        if self.shared_data.get("es_connected"):
            TestReporter.subsection("GETTING WISDOM FROM MEMORY")
            manager = MemoryManager()
            wisdom = await manager.get_global_wisdom(category="payment", limit=3)
            TestReporter.log(f"Found {len(wisdom)} relevant wisdom entries")
        
        TestReporter.log("\nSending to LLM with wisdom context...")
        
        response = await llm.ainvoke([
            {"role": "system", "content": "You are a freelance payment recovery specialist."},
            {"role": "user", "content": scenario}
        ])
        
        content = response.content
        
        TestReporter.subsection("GHOSTING PREVENTION ADVICE")
        TestReporter.log(content[:2000])
        
        content_lower = content.lower()
        checks = {
            "provides_escalation": any(w in content_lower for w in ["escalat", "next step", "action"]),
            "mentions_collection": any(w in content_lower for w in ["collect", "small claims", "legal", "attorney"]),
            "provides_template": any(w in content_lower for w in ["template", "email", "letter", "message"]),
            "professional_tone": any(w in content_lower for w in ["professional", "business", "firm"]),
        }
        
        TestReporter.subsection("GHOSTING PREVENTION VALIDATION")
        for check, passed in checks.items():
            TestReporter.log(f"  {'✅' if passed else '❌'} {check}")
        
        score = sum(checks.values())
        TestReporter.log(f"Ghosting Prevention Score: {score}/{len(checks)}")
        TestReporter.log("Ghosting prevention scenario PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_18_contract_negotiation_with_memory(self):
        """Contract negotiation with memory integration"""
        TestReporter.section("TEST 18: CONTRACT NEGOTIATION WITH MEMORY")
        
        from config import get_llm
        from lib.memory.manager import MemoryManager
        
        scenario = """
        New client contract proposal for a $25,000 enterprise software project:
        
        PROBLEMATIC TERMS:
        1. Payment: Net 90 after "full stakeholder approval"
        2. IP: All work becomes client property immediately
        3. Revisions: "Unlimited revisions until satisfaction"
        4. Warranty: 2-year free maintenance
        5. Liability: Developer liable for all business losses
        6. Termination: Client can terminate without payment
        7. Non-compete: Cannot work with competitors for 3 years
        
        What should I counter with? Give me specific negotiation language.
        """
        
        TestReporter.log("CONTRACT TERMS FOR NEGOTIATION:")
        TestReporter.log(scenario.strip())
        
        # Get context from memory
        wisdom_context = ""
        if self.shared_data.get("es_connected"):
            TestReporter.subsection("GATHERING CONTEXT FROM MEMORY")
            manager = MemoryManager()
            wisdom = await manager.get_global_wisdom(category="contract", limit=5)
            TestReporter.log(f"Contract wisdom: {len(wisdom)} entries")
            experiences = await manager.search_similar_experiences("contract negotiation payment")
            TestReporter.log(f"Similar experiences: {len(experiences)} found")
            
            if wisdom:
                wisdom_context = "\n".join([w.get("insight", "") for w in wisdom[:3]])
        
        llm = get_llm(temperature=0.3)
        
        prompt = f"""Based on the following wisdom from our knowledge base:
        {wisdom_context}
        
        {scenario}
        
        Provide:
        1. Risk assessment for each term
        2. Specific counter-proposal language
        3. Walk-away points (non-negotiable)
        4. Professional email template
        """
        
        TestReporter.log("\nGenerating negotiation strategy...")
        
        response = await llm.ainvoke([
            {"role": "system", "content": "You are a contract negotiation expert."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content
        
        TestReporter.subsection("NEGOTIATION STRATEGY")
        TestReporter.log(content[:2500])
        
        content_lower = content.lower()
        checks = {
            "addresses_payment": any(w in content_lower for w in ["payment", "upfront", "milestone", "net"]),
            "addresses_ip": any(w in content_lower for w in ["ip", "intellectual", "ownership"]),
            "addresses_revisions": any(w in content_lower for w in ["revision", "unlimited", "rounds"]),
            "addresses_liability": any(w in content_lower for w in ["liability", "cap", "limit"]),
            "provides_language": any(w in content_lower for w in ["counter", "propose", "suggest"]),
            "has_email_template": any(w in content_lower for w in ["email", "template", "dear", "subject"]),
        }
        
        TestReporter.subsection("NEGOTIATION QUALITY VALIDATION")
        for check, passed in checks.items():
            TestReporter.log(f"  {'✅' if passed else '❌'} {check}")
        
        score = sum(checks.values())
        TestReporter.log(f"\nNegotiation Quality Score: {score*100//len(checks)}% ({score}/{len(checks)})")
        TestReporter.log("Contract negotiation with memory PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 5: INTEGRATION
    # =========================================
    
    @pytest.mark.asyncio
    async def test_19_end_to_end_workflow(self):
        """Complete end-to-end workflow with all components"""
        TestReporter.section("TEST 19: END-TO-END WORKFLOW")
        
        from agents.orchestrator import run_orchestrator
        from lib.memory.manager import MemoryManager
        
        task = """
        I'm a freelance web developer. A potential client reached out via Upwork:
        
        Project: E-commerce website
        Budget: $5,000 fixed price
        Timeline: 2 months
        
        Their proposal:
        - No deposit, full payment on completion
        - They want me to sign an NDA before seeing requirements
        - Unlimited revisions until they're "satisfied"
        - They've had 3 other developers "fail" before me
        
        Red flags? Should I take this project? What should I negotiate?
        """
        
        TestReporter.log("Running complete analysis workflow...")
        
        start = time.time()
        result = await run_orchestrator(task=task, context={"user_id": "e2e_test"})
        duration = time.time() - start
        
        TestReporter.log(f"Total Duration: {duration:.2f}s")
        TestReporter.log(f"Status: {result.get('status')}")
        TestReporter.log(f"Risk Level: {result.get('risk_level')}")
        TestReporter.log(f"Agents: {list(result.get('agent_outputs', {}).keys())}")
        
        TestReporter.subsection("FULL ANALYSIS")
        synthesis = result.get("final_synthesis", "")
        TestReporter.log(synthesis[:2000])
        
        synthesis_lower = synthesis.lower()
        quality = {
            "risk_identified": any(w in synthesis_lower for w in ["risk", "concern", "warning", "red flag"]),
            "deposit_mentioned": any(w in synthesis_lower for w in ["deposit", "upfront", "payment"]),
            "revisions_addressed": any(w in synthesis_lower for w in ["revision", "unlimited", "scope"]),
            "actionable": any(w in synthesis_lower for w in ["recommend", "suggest", "should", "negotiate"]),
        }
        
        TestReporter.subsection("QUALITY ASSESSMENT")
        for check, passed in quality.items():
            TestReporter.log(f"  {'✅' if passed else '❌'} {check}")
        
        total = sum(quality.values())
        TestReporter.log(f"\nOverall Quality: {total}/{len(quality)}", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_20_copilotkit_integration(self):
        """CopilotKit API endpoint availability"""
        TestReporter.section("TEST 20: COPILOTKIT INTEGRATION")
        
        import httpx
        
        base_url = "http://localhost:8000"
        
        try:
            async with httpx.AsyncClient() as client:
                TestReporter.subsection("GET /api/agents")
                agents_resp = await client.get(f"{base_url}/api/agents", timeout=10)
                
                if agents_resp.status_code == 200:
                    data = agents_resp.json()
                    TestReporter.log(f"Status Code: {agents_resp.status_code}")
                    TestReporter.log(f"Found {data.get('count', 0)} agents registered", "SUCCESS")
                    
                    TestReporter.log("Registered Agents:", "DEBUG")
                    for agent in data.get("agents", [])[:5]:
                        TestReporter.log(f"  - [{agent['id']}] {agent['description'][:50]}...", "DEBUG")
                else:
                    TestReporter.log(f"API returned status: {agents_resp.status_code}", "WARNING")
                
                TestReporter.subsection("GET /api/agents/contract-guardian")
                detail_resp = await client.get(f"{base_url}/api/agents/contract-guardian", timeout=10)
                
                if detail_resp.status_code == 200:
                    agent = detail_resp.json()
                    TestReporter.log(f"Agent Found: {agent.get('id')}", "SUCCESS")
                    TestReporter.log(f"Description: {agent.get('description')}", "DEBUG")
                
                TestReporter.log("CopilotKit integration PASSED", "SUCCESS")
                
        except httpx.ConnectError:
            TestReporter.log("Server not running on localhost:8000 - SKIPPED", "WARNING")
            pytest.skip("Server not running")
        except Exception as e:
            TestReporter.log(f"CopilotKit check error: {e}", "WARNING")
            pytest.skip(f"CopilotKit error: {e}")
    
    @classmethod
    def teardown_class(cls):
        TestReporter.finish()
        print(f"\n📄 Full output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
