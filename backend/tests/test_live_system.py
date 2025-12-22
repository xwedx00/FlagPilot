"""
FlagPilot Live Integration Test - Multi-Venv Architecture
============================================================
Comprehensive test that validates the entire system including:
1. Elasticsearch Memory System (User Profiles, Chat History, Global Wisdom)
2. API Endpoints (Health, Agents, CopilotKit)
3. Subprocess Runners for isolated venvs

Output saved to test_live_output.txt
"""

import pytest
import asyncio
import time
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
from fastapi.testclient import TestClient

# Output file for test results
OUTPUT_FILE = "test_live_output.txt"


def log_output(message: str, level: str = "INFO", console: bool = True):
    """Write to output file with timestamp and log level"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    formatted = f"[{timestamp}] [{level}] {message}"
    
    if console:
        if level == "ERROR":
            print(f"\033[91m{formatted}\033[0m")
        elif level == "WARNING":
            print(f"\033[93m{formatted}\033[0m")
        elif level == "SUCCESS":
            print(f"\033[92m{formatted}\033[0m")
        elif level == "DEBUG":
            print(f"\033[90m{formatted}\033[0m")
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
    Live Integration Test Suite for Multi-Venv Architecture
    Tests: API, Memory System, Runners
    """
    
    @classmethod
    def setup_class(cls):
        """Initialize test output file"""
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("  FLAGPILOT LIVE INTEGRATION TEST - MULTI-VENV EDITION\n")
            f.write(f"  Started: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
        
        cls.shared_data = {}
        
        # Initialize TestClient
        from main import app
        cls.client = TestClient(app)
    
    # =========================================
    # SECTION 1: Environment & Health Checks
    # =========================================
    
    @pytest.mark.asyncio
    async def test_01_environment_check(self):
        """Test 1: Verify environment variables are configured"""
        log_section("TEST 1: ENVIRONMENT CHECK")
        
        from config import settings
        
        checks = {
            "OPENROUTER_API_KEY": bool(settings.OPENROUTER_API_KEY),
            "OPENROUTER_MODEL": bool(settings.OPENROUTER_MODEL),
            "ES_HOST": bool(settings.ES_HOST),
            "ES_PORT": bool(settings.ES_PORT),
            "REDIS_URL": bool(settings.REDIS_URL),
        }
        
        log_output(f"OpenRouter Model: {settings.OPENROUTER_MODEL}", "INFO")
        log_output(f"ES Host: {settings.ES_HOST}:{settings.ES_PORT}", "INFO")
        
        for name, is_set in checks.items():
            status = "✅ SET" if is_set else "❌ MISSING"
            log_output(f"  {name}: {status}", "INFO")
        
        log_output("Environment check PASSED", "SUCCESS")
    
    def test_02_api_health(self):
        """Test 2: Verify API health endpoint"""
        log_section("TEST 2: API HEALTH CHECK")
        
        response = self.client.get("/health")
        log_output(f"Status Code: {response.status_code}", "INFO")
        
        assert response.status_code == 200, "Health endpoint failed"
        
        data = response.json()
        log_json(data, "Health Response")
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert len(data.get("agents", [])) > 0
        
        self.shared_data["api_healthy"] = True
        log_output(f"API Version: {data['version']}", "SUCCESS")
        log_output(f"Agents Loaded: {len(data.get('agents', []))}", "SUCCESS")
        log_output("API health check PASSED", "SUCCESS")
    
    def test_03_agents_list(self):
        """Test 3: Verify agents list endpoint"""
        log_section("TEST 3: AGENTS LIST")
        
        response = self.client.get("/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        agents = data.get("agents", [])
        count = data.get("count", 0)
        
        log_output(f"Total Agents: {count}", "INFO")
        
        for agent in agents[:5]:
            log_output(f"  - {agent['id']}: {agent['name']}", "DEBUG")
        
        if count > 5:
            log_output(f"  ... and {count - 5} more", "DEBUG")
        
        # Verify key agents exist
        agent_ids = [a["id"] for a in agents]
        key_agents = ["contract-guardian", "job-authenticator", "flagpilot-orchestrator"]
        
        for key in key_agents:
            if key in agent_ids:
                log_output(f"  ✅ {key}", "SUCCESS")
            else:
                log_output(f"  ❌ {key} MISSING", "WARNING")
        
        assert count >= 10, f"Expected 10+ agents, got {count}"
        log_output("Agents list PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 2: Elasticsearch Memory Tests
    # =========================================
    
    @pytest.mark.asyncio
    async def test_04_elasticsearch_connection(self):
        """Test 4: Verify Elasticsearch connection via MemoryManager"""
        log_section("TEST 4: ELASTICSEARCH CONNECTION")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        health = manager.health_check()
        
        log_json(health, "ES Health")
        
        if health["connected"]:
            log_output(f"Cluster: {health.get('cluster_name', 'N/A')}", "INFO")
            log_output(f"Version: {health.get('version', 'N/A')}", "INFO")
            
            stats = manager.get_stats()
            log_output("Index Stats:", "INFO")
            for index, count in stats.items():
                log_output(f"  {index}: {count} docs", "DEBUG")
            
            self.shared_data["es_connected"] = True
            log_output("Elasticsearch connection PASSED", "SUCCESS")
        else:
            log_output(f"ES not connected: {health.get('error', 'Unknown')}", "WARNING")
            pytest.skip("Elasticsearch not available")
    
    @pytest.mark.asyncio
    async def test_05_user_profile_crud(self):
        """Test 5: User Profile CRUD operations"""
        log_section("TEST 5: USER PROFILE CRUD")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        if not manager.connected:
            pytest.skip("Elasticsearch not connected")
        
        test_user_id = f"test_user_{int(time.time())}"
        
        # CREATE
        log_subsection("CREATE Profile")
        result = await manager.update_user_profile(
            user_id=test_user_id,
            summary="Experienced freelancer, prefers fixed-price contracts, cautious about scope creep",
            preferences={"rate_min": 50, "avoid_clients": ["lowballers"]}
        )
        log_output(f"Create result: {result}", "INFO")
        assert result, "Failed to create profile"
        
        # READ
        log_subsection("READ Profile")
        profile = await manager.get_user_profile(test_user_id)
        log_json(profile, "Profile")
        assert profile["user_id"] == test_user_id
        assert "freelancer" in profile["summary"].lower()
        
        # UPDATE
        log_subsection("UPDATE Profile")
        result = await manager.update_user_profile(
            user_id=test_user_id,
            summary=profile["summary"] + " Recently added web development skills."
        )
        assert result
        
        updated = await manager.get_user_profile(test_user_id)
        assert "web development" in updated["summary"].lower()
        log_output("Profile updated successfully", "SUCCESS")
        
        log_output("User Profile CRUD PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_06_chat_history(self):
        """Test 6: Chat History storage and retrieval"""
        log_section("TEST 6: CHAT HISTORY")
        
        from lib.memory.manager import MemoryManager
        import uuid
        
        manager = MemoryManager()
        if not manager.connected:
            pytest.skip("Elasticsearch not connected")
        
        test_user_id = f"chat_test_{int(time.time())}"
        session_id = str(uuid.uuid4())
        
        # Save messages
        log_subsection("SAVE Messages")
        messages = [
            ("user", "I need help reviewing a contract"),
            ("assistant", "I'd be happy to help! Please share the contract details."),
            ("user", "The client wants 100% payment on completion with no deposit"),
            ("assistant", "That's a red flag. I recommend negotiating a deposit...")
        ]
        
        for role, content in messages:
            chat_id = await manager.save_chat(
                user_id=test_user_id,
                role=role,
                content=content,
                session_id=session_id,
                agent_id="contract-guardian"
            )
            log_output(f"Saved {role} message: {chat_id[:8]}...", "DEBUG")
        
        # Wait for ES indexing
        await asyncio.sleep(1)
        
        # Retrieve history
        log_subsection("RETRIEVE History")
        history = await manager.get_chat_history(test_user_id, session_id)
        log_output(f"Retrieved {len(history)} messages", "INFO")
        
        for msg in history:
            log_output(f"  [{msg['role']}]: {msg['content'][:50]}...", "DEBUG")
        
        assert len(history) >= 4, f"Expected 4+ messages, got {len(history)}"
        
        # Get sessions
        log_subsection("GET Sessions")
        sessions = await manager.get_recent_sessions(test_user_id)
        log_output(f"Sessions: {sessions}", "DEBUG")
        assert session_id in sessions
        
        log_output("Chat History PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_07_global_wisdom(self):
        """Test 7: Global Wisdom storage and retrieval"""
        log_section("TEST 7: GLOBAL WISDOM")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        if not manager.connected:
            pytest.skip("Elasticsearch not connected")
        
        # Add wisdom entries
        log_subsection("ADD Wisdom")
        wisdom_entries = [
            ("contract", "Always request a deposit before starting work", ["payment", "deposit"]),
            ("contract", "Define scope clearly to avoid scope creep", ["scope", "boundaries"]),
            ("scam", "Be wary of clients who contact via WhatsApp only", ["red-flag", "communication"]),
            ("negotiation", "Counter low offers with value justification", ["pricing", "rates"]),
        ]
        
        for category, insight, tags in wisdom_entries:
            result = await manager.add_wisdom(
                category=category,
                insight=insight,
                tags=tags,
                confidence=0.7
            )
            log_output(f"Added: {category} - {insight[:40]}...", "DEBUG")
        
        await asyncio.sleep(1)
        
        # Search wisdom
        log_subsection("SEARCH Wisdom")
        
        # By category
        contract_wisdom = await manager.get_global_wisdom(category="contract")
        log_output(f"Contract wisdom: {len(contract_wisdom)} entries", "INFO")
        
        # By query
        deposit_wisdom = await manager.get_global_wisdom(query="deposit payment")
        log_output(f"Deposit wisdom: {len(deposit_wisdom)} entries", "INFO")
        
        if deposit_wisdom:
            log_json(deposit_wisdom[0], "Top Result")
        
        assert len(contract_wisdom) >= 2, "Expected 2+ contract wisdom entries"
        
        log_output("Global Wisdom PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_08_experience_gallery(self):
        """Test 8: Experience Gallery (shared learnings)"""
        log_section("TEST 8: EXPERIENCE GALLERY")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        if not manager.connected:
            pytest.skip("Elasticsearch not connected")
        
        test_user_id = f"exp_test_{int(time.time())}"
        
        # Save experiences
        log_subsection("SAVE Experiences")
        experiences = [
            {
                "task": "Client wanted unlimited revisions but I set a cap of 3",
                "outcome": "Client agreed after I explained revision policy",
                "lesson": "Set clear revision limits upfront to avoid scope creep",
                "score": 1
            },
            {
                "task": "Detected a scam job posting with upfront fee request",
                "outcome": "Avoided the scam by recognizing red flags",
                "lesson": "Never pay upfront fees for job opportunities",
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
            log_output(f"Saved: {exp['lesson'][:40]}...", "DEBUG")
        
        await asyncio.sleep(1)
        
        # Search similar
        log_subsection("SEARCH Similar")
        similar = await manager.search_similar_experiences("revision limits scope creep")
        log_output(f"Found {len(similar)} similar experiences", "INFO")
        
        if similar:
            log_json(similar[0], "Top Match")
        
        log_output("Experience Gallery PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 3: Subprocess Runners
    # =========================================
    
    def test_09_runners_exist(self):
        """Test 9: Verify subprocess runners are importable"""
        log_section("TEST 9: SUBPROCESS RUNNERS")
        
        runners = []
        
        try:
            from lib.runners.metagpt_runner import MetaGPTRunner
            runners.append(("MetaGPT", MetaGPTRunner))
            log_output("  ✅ MetaGPTRunner", "SUCCESS")
        except ImportError as e:
            log_output(f"  ❌ MetaGPTRunner: {e}", "ERROR")
        
        try:
            from lib.runners.ragflow_runner import RAGFlowRunner
            runners.append(("RAGFlow", RAGFlowRunner))
            log_output("  ✅ RAGFlowRunner", "SUCCESS")
        except ImportError as e:
            log_output(f"  ❌ RAGFlowRunner: {e}", "ERROR")
        
        try:
            from lib.runners.copilotkit_runner import CopilotKitRunner
            runners.append(("CopilotKit", CopilotKitRunner))
            log_output("  ✅ CopilotKitRunner", "SUCCESS")
        except ImportError as e:
            log_output(f"  ❌ CopilotKitRunner: {e}", "ERROR")
        
        assert len(runners) == 3, f"Expected 3 runners, got {len(runners)}"
        log_output("Subprocess Runners PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 4: API Stress Tests
    # =========================================
    
    def test_10_api_stress(self):
        """Test 10: API stress test with multiple concurrent requests"""
        log_section("TEST 10: API STRESS TEST")
        
        import concurrent.futures
        
        endpoints = [
            ("/health", "GET"),
            ("/api/agents", "GET"),
            ("/api/agents/contract-guardian", "GET"),
            ("/", "GET"),
        ]
        
        results = {"success": 0, "failed": 0}
        start_time = time.time()
        
        def make_request(endpoint, method):
            try:
                if method == "GET":
                    resp = self.client.get(endpoint)
                else:
                    resp = self.client.post(endpoint, json={})
                
                return resp.status_code < 500
            except:
                return False
        
        # Sequential stress (10 requests per endpoint)
        log_subsection("Sequential Requests")
        for endpoint, method in endpoints:
            for _ in range(10):
                if make_request(endpoint, method):
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        duration = time.time() - start_time
        total = results["success"] + results["failed"]
        rps = total / duration if duration > 0 else 0
        
        log_output(f"Total Requests: {total}", "INFO")
        log_output(f"Successful: {results['success']}", "SUCCESS")
        log_output(f"Failed: {results['failed']}", "WARNING" if results["failed"] > 0 else "DEBUG")
        log_output(f"Duration: {duration:.2f}s", "INFO")
        log_output(f"RPS: {rps:.1f}", "INFO")
        
        assert results["success"] >= 35, f"Too many failures: {results['failed']}"
        log_output("API Stress Test PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 5: Memory Stress Test
    # =========================================
    
    @pytest.mark.asyncio
    async def test_11_memory_stress(self):
        """Test 11: Memory system stress test"""
        log_section("TEST 11: MEMORY STRESS TEST")
        
        from lib.memory.manager import MemoryManager
        
        manager = MemoryManager()
        if not manager.connected:
            pytest.skip("Elasticsearch not connected")
        
        test_user_id = f"stress_{int(time.time())}"
        start_time = time.time()
        
        # Write 50 chat messages rapidly
        log_subsection("WRITE Stress (50 messages)")
        write_success = 0
        
        for i in range(50):
            chat_id = await manager.save_chat(
                user_id=test_user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Stress test message {i}: " + "lorem ipsum " * 10,
                session_id=f"stress_session_{i // 10}"
            )
            if chat_id:
                write_success += 1
        
        log_output(f"Write success rate: {write_success}/50", "INFO")
        
        # Wait for indexing
        await asyncio.sleep(2)
        
        # Read stress
        log_subsection("READ Stress")
        history = await manager.get_chat_history(test_user_id, limit=100)
        log_output(f"Retrieved: {len(history)} messages", "INFO")
        
        sessions = await manager.get_recent_sessions(test_user_id, limit=10)
        log_output(f"Sessions found: {len(sessions)}", "INFO")
        
        duration = time.time() - start_time
        log_output(f"Total duration: {duration:.2f}s", "INFO")
        
        assert write_success >= 45, f"Write failures: {50 - write_success}"
        assert len(history) >= 40, f"Read failures: expected 40+, got {len(history)}"
        
        log_output("Memory Stress Test PASSED", "SUCCESS")
    
    @classmethod
    def teardown_class(cls):
        """Final summary and cleanup"""
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"  TEST SUITE COMPLETED: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n")
        
        print(f"\n\n📄 Full output saved to: {OUTPUT_FILE}")
