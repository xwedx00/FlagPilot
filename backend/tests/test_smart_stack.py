"""
Smart-Stack Feature Test Suite v6.1
===================================
Tests all Smart-Stack features: PostgresCheckpointer, Long-term Memory, LLM Router, Elasticsearch

Run: python tests/test_smart_stack.py
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SmartStackTester:
    """Comprehensive Smart-Stack feature tester"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    def log(self, msg: str, level: str = "INFO"):
        """Print formatted log message"""
        icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        icon = icons.get(level, "•")
        print(f"{icon} {msg}")
    
    def section(self, title: str):
        """Print section header"""
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")

    def test_environment(self):
        """Test environment variables"""
        self.section("Environment Check")
        
        vars_to_check = [
            ("DATABASE_URL", True),
            ("OPENROUTER_API_KEY", True),
            ("LANGSMITH_API_KEY", False),
            ("REDIS_URL", False),
            ("ES_HOST", False),
        ]
        
        for var, required in vars_to_check:
            value = os.environ.get(var)
            status = "Set" if value else "Missing"
            level = "PASS" if value else ("FAIL" if required else "WARN")
            self.log(f"{var}: {status}", level)
            if required and not value:
                self.results["environment"] = f"FAIL: {var} missing"
        
        if "environment" not in self.results:
            self.results["environment"] = "PASS"

    def test_checkpointer(self):
        """Test AsyncPostgresSaver checkpointer"""
        self.section("Checkpointer Test (AsyncPostgresSaver)")
        
        try:
            from lib.persistence import get_checkpointer
            cp = get_checkpointer()
            cp_type = type(cp).__name__
            
            self.log(f"Checkpointer Type: {cp_type}")
            
            # Check if async-capable
            is_async = "Async" in cp_type or cp_type == "AsyncPostgresSaver"
            is_postgres = "Postgres" in cp_type or "PostgresSaver" in cp_type
            
            if is_postgres:
                self.log("Using PostgresSaver - state persists!", "PASS")
                self.results["checkpointer"] = "PASS (PostgresSaver)"
            else:
                self.log("Using MemorySaver - state will be lost on restart", "WARN")
                self.results["checkpointer"] = "WARN (MemorySaver)"
                
        except Exception as e:
            self.log(f"Checkpointer Error: {e}", "FAIL")
            self.results["checkpointer"] = f"FAIL: {e}"

    def test_long_term_memory(self):
        """Test PostgresStore for long-term memory"""
        self.section("Long-Term Memory Test (PostgresStore)")
        
        try:
            from lib.persistence import get_long_term_memory
            ltm = get_long_term_memory()
            
            store_type = type(ltm.store).__name__
            is_persistent = ltm.is_persistent
            
            self.log(f"Store Type: {store_type}")
            self.log(f"Is Persistent: {is_persistent}")
            
            # Test memory operations
            test_user = "test_user_smart_stack"
            test_key = "test_memory"
            test_data = {"message": "Hello from test!", "timestamp": str(datetime.now())}
            
            # Remember
            result = ltm.remember(test_user, test_key, test_data)
            self.log(f"Remember: {result}")
            
            # Recall
            recalled = ltm.get_memory(test_user, test_key)
            self.log(f"Recall: {recalled}")
            
            if result and recalled:
                self.log("Memory operations working", "PASS")
                self.results["long_term_memory"] = "PASS" if is_persistent else "WARN (InMemoryStore)"
            else:
                self.results["long_term_memory"] = "FAIL: Operations failed"
                
        except Exception as e:
            self.log(f"Long-term Memory Error: {e}", "FAIL")
            self.results["long_term_memory"] = f"FAIL: {e}"

    def test_llm_router(self):
        """Test LLM Router for semantic agent selection"""
        self.section("LLM Router Test")
        
        try:
            from agents.router import AGENT_REGISTRY, fallback_keyword_route
            
            num_agents = len(AGENT_REGISTRY)
            self.log(f"Agents in Registry: {num_agents}")
            
            # Test keyword routing (sync fallback)
            test_cases = [
                ("I need to analyze this contract", ["contract-guardian"]),
                ("Is this job posting a scam?", ["job-authenticator", "risk-advisor"]),
                ("Help me with payment collection", ["payment-enforcer"]),
                ("I need negotiation advice", ["negotiation-assistant"]),
            ]
            
            all_passed = True
            for task, expected in test_cases:
                result = fallback_keyword_route(task)
                has_expected = any(e in result for e in expected)
                status = "PASS" if has_expected else "FAIL"
                self.log(f"  Route '{task[:30]}...' -> {result} [{status}]")
                if not has_expected:
                    all_passed = False
            
            if num_agents > 0 and all_passed:
                self.log("LLM Router working", "PASS")
                self.results["llm_router"] = f"PASS ({num_agents} agents)"
            else:
                self.results["llm_router"] = f"WARN: Some routes failed"
                
        except Exception as e:
            self.log(f"LLM Router Error: {e}", "FAIL")
            self.results["llm_router"] = f"FAIL: {e}"

    def test_elasticsearch(self):
        """Test Elasticsearch connection"""
        self.section("Elasticsearch Test")
        
        try:
            from elasticsearch import Elasticsearch
            
            es_host = os.environ.get("ES_HOST", "es01")
            es_port = os.environ.get("ES_PORT", "9200")
            
            es = Elasticsearch([f"http://{es_host}:{es_port}"])
            
            # Check cluster health
            health = es.cluster.health()
            cluster = health.get("cluster_name", "unknown")
            status = health.get("status", "unknown")
            
            self.log(f"Cluster: {cluster}")
            self.log(f"Status: {status}")
            
            if status in ["green", "yellow"]:
                self.log("Elasticsearch healthy", "PASS")
                self.results["elasticsearch"] = f"PASS ({status})"
            else:
                self.log(f"Elasticsearch status: {status}", "WARN")
                self.results["elasticsearch"] = f"WARN ({status})"
                
        except Exception as e:
            self.log(f"Elasticsearch Error: {e}", "FAIL")
            self.results["elasticsearch"] = f"FAIL: {e}"

    def test_agent_registry(self):
        """Test agent registry"""
        self.section("Agent Registry Test")
        
        try:
            from agents.agents import list_agents, get_agent
            
            agents = list_agents()
            num_agents = len(agents)
            
            self.log(f"Total Agents: {num_agents}")
            
            # List first 5
            for agent_id in list(agents)[:5]:
                agent = get_agent(agent_id)
                desc = agent.description[:40] if agent.description else "No description"
                self.log(f"  - {agent_id}: {desc}...")
            
            if num_agents > 5:
                self.log(f"  ... and {num_agents - 5} more")
            
            if num_agents >= 14:
                self.log(f"Agent registry OK ({num_agents} agents)", "PASS")
                self.results["agent_registry"] = f"PASS ({num_agents} agents)"
            else:
                self.log(f"Expected 14+ agents, got {num_agents}", "WARN")
                self.results["agent_registry"] = f"WARN ({num_agents} agents)"
                
        except Exception as e:
            self.log(f"Agent Registry Error: {e}", "FAIL")
            self.results["agent_registry"] = f"FAIL: {e}"

    def print_summary(self):
        """Print test summary"""
        self.section("TEST RESULTS SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v.startswith("PASS"))
        warned = sum(1 for v in self.results.values() if v.startswith("WARN"))
        failed = sum(1 for v in self.results.values() if v.startswith("FAIL"))
        
        for test, result in self.results.items():
            if result.startswith("PASS"):
                icon = "✅"
            elif result.startswith("WARN"):
                icon = "⚠️"
            else:
                icon = "❌"
            print(f"  {icon} {test}: {result}")
        
        print(f"\n{'='*50}")
        print(f"  Results: {passed} passed, {warned} warned, {failed} failed")
        print(f"  Duration: {(datetime.now() - self.start_time).total_seconds():.2f}s")
        print(f"{'='*50}")
        
        return failed == 0

    def run_all(self) -> bool:
        """Run all tests"""
        print("\n" + "="*50)
        print("  SMART-STACK FEATURE TEST SUITE v6.1")
        print(f"  Started: {self.start_time.isoformat()}")
        print("="*50)
        
        self.test_environment()
        self.test_checkpointer()
        self.test_long_term_memory()
        self.test_llm_router()
        self.test_elasticsearch()
        self.test_agent_registry()
        
        return self.print_summary()


def run_tests():
    """Entry point for test execution"""
    tester = SmartStackTester()
    success = tester.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
