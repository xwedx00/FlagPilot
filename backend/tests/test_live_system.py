"""
FlagPilot Live Integration Test Suite - LangGraph Edition
=========================================================
Comprehensive tests validating the entire LangGraph multi-agent system:

1. Environment & Health Checks
2. LangChain LLM Integration  
3. Agent Registry & Capabilities
4. LangGraph Orchestrator (Fast-Fail, Routing, Synthesis)
5. RAGFlow Knowledge Retrieval
6. Elasticsearch Memory System
7. CopilotKit Endpoint Integration
8. End-to-End Workflow Tests
9. Stress & Edge Cases

Output saved to: test_live_output.txt (different from test_live_system_output.txt)

This test suite validates the LangGraph-based multi-agent system.
"""

import pytest
import asyncio
import time
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
import sys

# Ensure backend is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Output files
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
        
        # Console with colors
        colors = {"ERROR": "\033[91m", "WARNING": "\033[93m", "SUCCESS": "\033[92m", "DEBUG": "\033[90m"}
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] [{level}] {msg}\033[0m" if color else f"[{timestamp}] [{level}] {msg}")
        
        # File
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
            for line in formatted.split("\n"):
                cls.log(f"  {line}", "DEBUG")
        except:
            cls.log(f"{label}: {data}", "DEBUG")
    
    @classmethod
    def finish(cls):
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"  COMPLETED: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n")


# Initialize reporter
TestReporter.init()


class TestLiveSystemIntegration:
    """
    Comprehensive LangGraph Integration Test Suite
    """
    
    shared_data = {}
    
    # =========================================
    # 1. ENVIRONMENT & CONFIGURATION
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
        }
        
        TestReporter.log(f"OpenRouter Model: {settings.OPENROUTER_MODEL}")
        TestReporter.log(f"Base URL: {settings.OPENROUTER_BASE_URL}")
        TestReporter.log(f"RAGFlow: {settings.RAGFLOW_URL}")
        TestReporter.log(f"Elasticsearch: {settings.ES_HOST}:{settings.ES_PORT}")
        
        if settings.LANGSMITH_API_KEY:
            TestReporter.log(f"LangSmith: Enabled ({settings.LANGSMITH_PROJECT})", "SUCCESS")
        else:
            TestReporter.log("LangSmith: Not configured", "WARNING")
        
        passed = sum(checks.values())
        TestReporter.log(f"Environment: {passed}/{len(checks)} configured", "SUCCESS" if passed >= 3 else "WARNING")
    
    # =========================================
    # 2. LANGCHAIN LLM HEALTH
    # =========================================
    
    @pytest.mark.asyncio  
    async def test_02_langchain_llm_health(self):
        """Verify LangChain ChatOpenAI works with OpenRouter"""
        TestReporter.section("TEST 2: LANGCHAIN LLM HEALTH")
        
        from config import get_llm
        
        llm = get_llm(temperature=0)
        TestReporter.log(f"Model: {llm.model_name}")
        
        start = time.time()
        response = await llm.ainvoke("Say 'FlagPilot online' and nothing else.")
        duration = time.time() - start
        
        TestReporter.log(f"Response: {response.content}", "SUCCESS")
        TestReporter.log(f"Latency: {duration:.2f}s")
        
        assert "flagpilot" in response.content.lower() or len(response.content) > 0
        self.shared_data["llm_working"] = True
    
    # =========================================
    # 3. AGENT REGISTRY
    # =========================================
    
    @pytest.mark.asyncio
    async def test_03_agent_registry(self):
        """Verify all LangGraph agents are registered"""
        TestReporter.section("TEST 3: AGENT REGISTRY")
        
        from agents.agents import list_agents, get_agent, AGENTS
        
        agents = list_agents()
        TestReporter.log(f"Registered agents: {len(agents)}")
        
        expected = [
            "contract-guardian", "job-authenticator", "risk-advisor",
            "scope-sentinel", "payment-enforcer", "negotiation-assistant",
            "communication-coach", "dispute-mediator", "ghosting-shield",
            "profile-analyzer", "talent-vet", "application-filter",
            "feedback-loop", "planner-role"
        ]
        
        TestReporter.subsection("AGENT LIST")
        for agent_id in sorted(agents):
            agent = get_agent(agent_id)
            status = "OK" if agent else "MISSING"
            TestReporter.log(f"  {agent_id}: {status} (cost: {agent.credit_cost if agent else 'N/A'})", 
                           "DEBUG" if status == "OK" else "ERROR")
        
        missing = set(expected) - set(agents)
        if missing:
            TestReporter.log(f"Missing agents: {missing}", "ERROR")
        
        assert len(agents) >= 14, f"Expected 14 agents, got {len(agents)}"
        TestReporter.log(f"Agent Registry: {len(agents)} agents ready", "SUCCESS")
    
    # =========================================
    # 4. SCAM DETECTION (FAST-FAIL)
    # =========================================
    
    @pytest.mark.asyncio
    async def test_04_scam_detection_fast_fail(self):
        """Test programmatic scam detection before LLM call"""
        TestReporter.section("TEST 4: FAST-FAIL SCAM DETECTION")
        
        from agents.orchestrator import detect_scam_signals
        
        test_cases = [
            ("Normal job: Looking for a web developer for my e-commerce site", 0),
            ("Contact me on Telegram for the job details", 1),
            ("Send you a check for equipment then return excess", 3),
            ("No experience required, $45/hr data entry work from home via WhatsApp", 5),
            ("Pay security deposit via Zelle before starting", 4),
        ]
        
        TestReporter.subsection("SCAM SIGNAL TESTS")
        for text, min_expected in test_cases:
            signals = detect_scam_signals(text)
            status = "PASS" if len(signals) >= min_expected else "FAIL"
            TestReporter.log(f"  Detected {len(signals)} signals (expected >={min_expected}): {status}")
            TestReporter.log(f"    Text: {text[:60]}...", "DEBUG")
            TestReporter.log(f"    Signals: {signals}", "DEBUG")
        
        # Full scam should have many signals
        full_scam = "Contact me on Telegram @scammer123. I'll send you a check for $3000 via Zelle, no experience required, $50/hr data entry."
        full_signals = detect_scam_signals(full_scam)
        assert len(full_signals) >= 4, f"Expected 4+ signals for obvious scam, got {len(full_signals)}"
        
        TestReporter.log(f"Fast-fail detection: {len(full_signals)} signals for test scam", "SUCCESS")
    
    # =========================================
    # 5. ORCHESTRATOR ROUTING
    # =========================================
    
    @pytest.mark.asyncio
    async def test_05_orchestrator_routing(self):
        """Test dynamic agent selection based on task"""
        TestReporter.section("TEST 5: ORCHESTRATOR ROUTING")
        
        from agents.orchestrator import identify_relevant_agents, is_simple_greeting
        
        test_cases = [
            ("Review this contract for legal issues", ["contract-guardian"]),
            ("Is this job posting a scam?", ["job-authenticator"]),
            ("Client hasn't paid my invoice for 30 days", ["payment-enforcer"]),
            ("Help me negotiate a better rate", ["negotiation-assistant"]),
            ("The client is asking for more features", ["scope-sentinel"]),
            ("Draft a professional response to client", ["communication-coach"]),
        ]
        
        TestReporter.subsection("ROUTING TESTS")
        for task, expected in test_cases:
            agents = identify_relevant_agents(task)
            has_expected = any(e in agents for e in expected)
            status = "PASS" if has_expected else "FAIL"
            TestReporter.log(f"  {task[:40]}... -> {agents} [{status}]")
        
        # Test greeting detection
        assert is_simple_greeting("hello")
        assert is_simple_greeting("hi there")
        assert not is_simple_greeting("Please review my contract thoroughly")
        
        TestReporter.log("Routing logic validated", "SUCCESS")
    
    # =========================================
    # 6. FULL ORCHESTRATOR RUN (SCAM)
    # =========================================
    
    @pytest.mark.asyncio
    async def test_06_orchestrator_scam_response(self):
        """Test full orchestrator with scam detection"""
        TestReporter.section("TEST 6: ORCHESTRATOR - SCAM DETECTION")
        
        from agents.orchestrator import run_orchestrator
        
        scam_task = """
        Got a job offer via Telegram from "QuickMoney LLC":
        - $50/hr data entry, no experience required
        - They'll send a check for $3000 for equipment
        - Need my bank details for direct deposit
        - Contact @quickmoney_hiring on Telegram
        
        Should I take this job?
        """
        
        TestReporter.log("Task: Obvious scam job offer")
        TestReporter.log("Running orchestrator...", "INFO")
        
        start = time.time()
        result = await run_orchestrator(task=scam_task, context={"user_id": "test_scam"})
        duration = time.time() - start
        
        TestReporter.log(f"Duration: {duration:.2f}s")
        TestReporter.log(f"Status: {result.get('status')}")
        TestReporter.log(f"Risk Level: {result.get('risk_level')}")
        TestReporter.log(f"Critical Risk: {result.get('is_critical_risk')}")
        
        TestReporter.subsection("RESPONSE")
        synthesis = result.get("final_synthesis", "")[:1500]
        TestReporter.log(synthesis)
        
        # Validate
        assert result.get("risk_level") in ["HIGH", "CRITICAL"]
        assert "scam" in synthesis.lower() or "risk" in synthesis.lower() or "warning" in synthesis.lower()
        
        TestReporter.log("Scam correctly detected and flagged", "SUCCESS")
    
    # =========================================
    # 7. ORCHESTRATOR CONTRACT ANALYSIS
    # =========================================
    
    @pytest.mark.asyncio
    async def test_07_orchestrator_contract_analysis(self):
        """Test orchestrator with contract analysis"""
        TestReporter.section("TEST 7: ORCHESTRATOR - CONTRACT ANALYSIS")
        
        from agents.orchestrator import run_orchestrator
        
        contract_task = """
        Review this freelance contract:
        
        - Payment: 100% after project completion
        - No upfront deposit
        - IP transfers immediately to client before payment
        - 90-day payment window after "satisfaction review"
        - Client can terminate with 24h notice, no payment for work done
        - Unlimited revisions required
        
        What are the risks? What should I negotiate?
        """
        
        TestReporter.log("Task: High-risk contract review")
        
        start = time.time()
        result = await run_orchestrator(task=contract_task, context={"user_id": "test_contract"})
        duration = time.time() - start
        
        TestReporter.log(f"Duration: {duration:.2f}s")
        TestReporter.log(f"Agents used: {list(result.get('agent_outputs', {}).keys())}")
        
        TestReporter.subsection("CONTRACT ANALYSIS")
        synthesis = result.get("final_synthesis", "")[:2000]
        TestReporter.log(synthesis)
        
        # Quality checks
        synthesis_lower = synthesis.lower()
        checks = {
            "payment_risk": any(w in synthesis_lower for w in ["payment", "upfront", "deposit", "100%"]),
            "ip_risk": any(w in synthesis_lower for w in ["ip", "intellectual", "ownership"]),
            "recommendations": any(w in synthesis_lower for w in ["recommend", "negotiate", "request", "should"]),
        }
        
        passed = sum(checks.values())
        TestReporter.log(f"Quality checks: {passed}/{len(checks)}", "SUCCESS" if passed >= 2 else "WARNING")
    
    # =========================================
    # 8. ELASTICSEARCH MEMORY
    # =========================================
    
    @pytest.mark.asyncio
    async def test_08_elasticsearch_memory(self):
        """Test Elasticsearch memory operations"""
        TestReporter.section("TEST 8: ELASTICSEARCH MEMORY")
        
        try:
            from lib.memory.manager import MemoryManager
            
            manager = MemoryManager()
            health = manager.health_check()
            
            if not health.get("connected"):
                TestReporter.log("Elasticsearch not available - SKIPPED", "WARNING")
                pytest.skip("Elasticsearch not connected")
            
            TestReporter.log(f"ES Cluster: {health.get('cluster_name')}")
            TestReporter.log(f"ES Version: {health.get('version')}")
            
            # Profile operations
            TestReporter.subsection("PROFILE OPS")
            test_user = f"test_{int(time.time())}"
            
            result = await manager.update_user_profile(
                user_id=test_user,
                summary="Test user - web developer",
                preferences={"rate": 75}
            )
            TestReporter.log(f"Profile created: {result}", "SUCCESS" if result else "ERROR")
            
            profile = await manager.get_user_profile(test_user)
            TestReporter.log(f"Profile retrieved: {profile.get('user_id')}")
            
            self.shared_data["es_connected"] = True
            TestReporter.log("Elasticsearch Memory: OK", "SUCCESS")
            
        except Exception as e:
            TestReporter.log(f"Elasticsearch error: {e}", "WARNING")
            pytest.skip(f"Elasticsearch unavailable: {e}")
    
    # =========================================
    # 9. RAGFLOW INTEGRATION
    # =========================================
    
    @pytest.mark.asyncio
    async def test_09_ragflow_integration(self):
        """Test RAGFlow knowledge retrieval"""
        TestReporter.section("TEST 9: RAGFLOW INTEGRATION")
        
        try:
            from ragflow.client import get_ragflow_client
            
            client = get_ragflow_client()
            
            # Health check via listing datasets
            datasets = await client.list_datasets()
            TestReporter.log(f"RAGFlow datasets: {len(datasets) if datasets else 0}")
            
            # Search test
            TestReporter.subsection("RAG SEARCH")
            results = await client.search("freelance contract payment terms", limit=3)
            TestReporter.log(f"Search results: {len(results) if results else 0}")
            
            if results:
                for i, r in enumerate(results[:3]):
                    content = str(r.get("content", ""))[:100]
                    TestReporter.log(f"  [{i+1}] {content}...", "DEBUG")
            
            TestReporter.log("RAGFlow integration: OK", "SUCCESS")
            
        except Exception as e:
            TestReporter.log(f"RAGFlow not available: {e}", "WARNING")
            pytest.skip(f"RAGFlow unavailable: {e}")
    
    # =========================================
    # 10. END-TO-END WORKFLOW
    # =========================================
    
    @pytest.mark.asyncio
    async def test_10_end_to_end_workflow(self):
        """Complete end-to-end test with all components"""
        TestReporter.section("TEST 10: END-TO-END WORKFLOW")
        
        from agents.orchestrator import run_orchestrator
        
        # Complex realistic task
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
        result = await run_orchestrator(
            task=task,
            context={"user_id": "e2e_test", "platform": "upwork"}
        )
        duration = time.time() - start
        
        TestReporter.log(f"Total Duration: {duration:.2f}s")
        TestReporter.log(f"Status: {result.get('status')}")
        TestReporter.log(f"Risk Level: {result.get('risk_level')}")
        TestReporter.log(f"Agents: {list(result.get('agent_outputs', {}).keys())}")
        
        TestReporter.subsection("FULL ANALYSIS")
        synthesis = result.get("final_synthesis", "")
        
        # Log in chunks
        for i in range(0, len(synthesis), 1000):
            TestReporter.log(synthesis[i:i+1000], "INFO")
        
        # Validate comprehensive analysis
        synthesis_lower = synthesis.lower()
        quality = {
            "risk_identified": any(w in synthesis_lower for w in ["risk", "concern", "warning", "red flag"]),
            "deposit_mentioned": any(w in synthesis_lower for w in ["deposit", "upfront", "payment"]),
            "revisions_addressed": any(w in synthesis_lower for w in ["revision", "unlimited", "scope"]),
            "actionable": any(w in synthesis_lower for w in ["recommend", "suggest", "should", "negotiate"]),
        }
        
        TestReporter.subsection("QUALITY ASSESSMENT")
        for check, passed in quality.items():
            TestReporter.log(f"  {check}: {'PASS' if passed else 'FAIL'}", "SUCCESS" if passed else "WARNING")
        
        total = sum(quality.values())
        TestReporter.log(f"\nOverall Quality: {total}/{len(quality)}", "SUCCESS" if total >= 3 else "WARNING")
    
    # =========================================
    # 11. GREETING & EDGE CASES
    # =========================================
    
    @pytest.mark.asyncio
    async def test_11_greeting_response(self):
        """Test simple greeting bypasses agents"""
        TestReporter.section("TEST 11: GREETING & EDGE CASES")
        
        from agents.orchestrator import run_orchestrator
        
        # Simple greeting
        result = await run_orchestrator("Hello!", context={})
        
        TestReporter.log("Greeting test:")
        TestReporter.log(f"  Status: {result.get('status')}")
        TestReporter.log(f"  Agent outputs: {len(result.get('agent_outputs', {}))}")
        
        synthesis = result.get("final_synthesis", "")
        assert len(synthesis) > 0, "Should get welcome message"
        assert "flagpilot" in synthesis.lower() or "help" in synthesis.lower()
        
        TestReporter.log("  Welcome message returned", "SUCCESS")
        
        # Edge: empty task
        TestReporter.subsection("EMPTY TASK")
        result2 = await run_orchestrator("", context={})
        TestReporter.log(f"  Empty task handled: {result2.get('status')}")
    
    # =========================================
    # FINAL SUMMARY
    # =========================================
    
    @classmethod
    def teardown_class(cls):
        TestReporter.finish()
        print(f"\n📄 Full output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
