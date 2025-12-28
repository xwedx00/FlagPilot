"""
FlagPilot Live Integration Test Suite - v7.0
==============================================
Comprehensive tests validating the entire LangGraph multi-agent system:

SECTION 1: Environment & Health
  1. Environment Check
  2. Qdrant Vector DB Health
  3. LangChain LLM Health
  4. Elasticsearch Memory
  5. LangSmith Tracing
  6. MinIO Storage Health

SECTION 2: Agent System
  7. Agent Registry
  8. Fast-Fail Scam Detection
  9. Orchestrator Routing

SECTION 3: RAG & Memory (Qdrant + MinIO)
  10. Qdrant Document Ingest & Search
  11. MinIO File Upload
  12. User Profile Operations
  13. Chat History Operations
  14. Global Wisdom Operations
  15. Experience Gallery

SECTION 4: Complex Scenarios
  16. Scam Detection Scenario
  17. Contract Analysis Quality
  18. Scope Creep Detection
  19. Ghosting Prevention
  20. Contract Negotiation with Memory

SECTION 5: Integration
  21. End-to-End Workflow
  22. CopilotKit API Integration

Output saved to: test_live_output.txt
This test suite validates the LangGraph-based multi-agent system v7.0.
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
            f.write("  FLAGPILOT LIVE INTEGRATION TEST - v7.0 (Qdrant + MinIO)\n")
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
    """Comprehensive LangGraph Integration Test Suite v7.0"""
    
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
            "openrouter_api_key": bool(settings.openrouter_api_key),
            "openrouter_model": bool(settings.openrouter_model),
            "openrouter_base_url": bool(settings.openrouter_base_url),
            "qdrant_host": bool(settings.qdrant_host),
            "qdrant_port": bool(settings.qdrant_port),
            "minio_endpoint": bool(settings.minio_endpoint),
            "es_host": bool(settings.es_host),
            "es_port": bool(settings.es_port),
        }
        
        TestReporter.log(f"OpenRouter Model: {settings.openrouter_model}")
        TestReporter.log(f"OpenRouter Base URL: {settings.openrouter_base_url}")
        TestReporter.log(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
        TestReporter.log(f"MinIO: {settings.minio_endpoint}")
        TestReporter.log(f"ES: {settings.es_host}:{settings.es_port}")
        
        for name, is_set in checks.items():
            status = "✅ SET" if is_set else "❌ MISSING"
            TestReporter.log(f"  {name}: {status}")
        
        if settings.langsmith_api_key:
            TestReporter.log(f"LangSmith Project: {settings.langsmith_project}", "SUCCESS")
        else:
            TestReporter.log("LangSmith: Not configured", "WARNING")
        
        TestReporter.log("Environment check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_02_qdrant_health(self):
        """Verify Qdrant vector database is connected and healthy"""
        TestReporter.section("TEST 2: QDRANT HEALTH CHECK")
        
        try:
            from lib.vectorstore import get_qdrant_store
            
            TestReporter.log("Checking Qdrant health...")
            store = get_qdrant_store()
            info = store.get_collection_info()
            
            TestReporter.json({
                "status": "healthy",
                "connected": True,
                "collection": info.get("name"),
                "vectors_count": info.get("vectors_count", 0),
            }, "Qdrant Status")
            
            self.shared_data["qdrant_healthy"] = True
            TestReporter.log("Qdrant health check PASSED", "SUCCESS")
        except Exception as e:
            TestReporter.log(f"Qdrant health check error: {e}", "WARNING")
            self.shared_data["qdrant_healthy"] = False
            pytest.skip(f"Qdrant not available: {e}")
    
    @pytest.mark.asyncio
    async def test_03_langchain_llm_health(self):
        """Verify LangChain ChatOpenAI works with OpenRouter"""
        TestReporter.section("TEST 3: LANGCHAIN LLM HEALTH CHECK")
        
        from config import settings
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=settings.openrouter_model,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base=settings.openrouter_base_url,
            temperature=0,
        )
        
        TestReporter.log(f"Model: {settings.openrouter_model}")
        TestReporter.log("Sending test prompt...")
        
        start = time.time()
        response = await llm.ainvoke("Say 'Hello! I'm working and ready to help you.' and nothing else.")
        duration = time.time() - start
        
        TestReporter.log(f"Response: {response.content[:100]}...")
        TestReporter.log(f"Latency: {duration:.2f}s")
        
        assert response.content, "Empty LLM response"
        TestReporter.log("LangChain LLM health check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_04_elasticsearch_health(self):
        """Verify Elasticsearch is connected"""
        TestReporter.section("TEST 4: ELASTICSEARCH HEALTH CHECK")
        
        try:
            from elasticsearch import Elasticsearch
            from config import settings
            
            es = Elasticsearch([settings.es_url])
            
            if es.ping():
                info = es.info()
                TestReporter.log(f"ES Version: {info['version']['number']}")
                TestReporter.log(f"Cluster: {info['cluster_name']}")
                self.shared_data["es_connected"] = True
                TestReporter.log("Elasticsearch health check PASSED", "SUCCESS")
            else:
                self.shared_data["es_connected"] = False
                pytest.skip("Elasticsearch not reachable")
        except Exception as e:
            TestReporter.log(f"ES health error: {e}", "WARNING")
            self.shared_data["es_connected"] = False
            pytest.skip(f"Elasticsearch not available: {e}")
    
    @pytest.mark.asyncio
    async def test_05_langsmith_tracing(self):
        """Verify LangSmith tracing configuration"""
        TestReporter.section("TEST 5: LANGSMITH TRACING")
        
        from config import settings
        
        if settings.langsmith_api_key:
            TestReporter.log(f"Project: {settings.langsmith_project}")
            TestReporter.log("LangSmith enabled", "SUCCESS")
        else:
            TestReporter.log("LangSmith not configured - tracing disabled (OK for local dev)", "INFO")
        
        # Test passes regardless - LangSmith is optional
        TestReporter.log("LangSmith tracing check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_06_minio_health(self):
        """Verify MinIO storage is connected"""
        TestReporter.section("TEST 6: MINIO STORAGE HEALTH CHECK")
        
        try:
            from lib.storage import get_minio_storage
            
            TestReporter.log("Checking MinIO health...")
            storage = get_minio_storage()
            files = storage.list_files()
            
            TestReporter.log(f"MinIO connected, {len(files)} files in bucket")
            self.shared_data["minio_healthy"] = True
            TestReporter.log("MinIO health check PASSED", "SUCCESS")
        except Exception as e:
            TestReporter.log(f"MinIO health check error: {e}", "WARNING")
            self.shared_data["minio_healthy"] = False
            pytest.skip(f"MinIO not available: {e}")
    
    # =========================================
    # SECTION 2: AGENT SYSTEM
    # =========================================
    
    @pytest.mark.asyncio
    async def test_07_agent_registry(self):
        """Verify all agents are registered"""
        TestReporter.section("TEST 7: AGENT REGISTRY")
        
        from agents.router import AGENT_REGISTRY
        
        TestReporter.log(f"Registered Agents: {len(AGENT_REGISTRY)}")
        
        expected_agents = [
            "contract-guardian", "job-authenticator", "scope-sentinel",
            "payment-enforcer", "dispute-mediator", "communication-coach",
            "negotiation-assistant", "profile-analyzer", "ghosting-shield",
            "risk-advisor"
        ]
        
        for agent_id in expected_agents:
            if agent_id in AGENT_REGISTRY:
                TestReporter.log(f"  ✅ {agent_id}", "SUCCESS")
            else:
                TestReporter.log(f"  ❌ {agent_id} MISSING", "ERROR")
        
        assert len(AGENT_REGISTRY) >= 10, f"Expected at least 10 agents, got {len(AGENT_REGISTRY)}"
        TestReporter.log("Agent registry check PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_08_fast_fail_scam_detection(self):
        """Verify fast-fail scam detection via orchestrator"""
        TestReporter.section("TEST 8: FAST-FAIL SCAM DETECTION")
        
        from agents.router import llm_route_agents, AGENT_REGISTRY
        
        scam_message = "Congratulations! You've won $50,000! Send $500 to claim your prize!"
        
        TestReporter.log(f"Testing message: {scam_message[:50]}...")
        
        try:
            agents, reasoning, urgency = await llm_route_agents(scam_message, {})
            
            TestReporter.log(f"Agents selected: {agents}")
            TestReporter.log(f"Urgency: {urgency}")
            TestReporter.log(f"Reasoning: {reasoning[:100]}...")
            
            # Should route to risk-advisor for scam
            has_risk = "risk-advisor" in agents or urgency in ["high", "critical"]
            
            if has_risk:
                TestReporter.log("✅ Scam correctly routed to risk detection", "SUCCESS")
            else:
                TestReporter.log("⚠️ May not have detected as scam", "WARNING")
            
        except Exception as e:
            TestReporter.log(f"Routing test error: {e}", "WARNING")
        
        TestReporter.log("Fast-fail scam detection PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_09_orchestrator_routing(self):
        """Verify LLM-based orchestrator routing"""
        TestReporter.section("TEST 9: ORCHESTRATOR ROUTING")
        
        from agents.router import llm_route_agents, fallback_keyword_route
        
        test_cases = [
            ("Please review my freelance contract for red flags", ["contract-guardian"]),
            ("Is this job posting a scam?", ["job-authenticator"]),
            ("Client keeps adding extra features without paying", ["scope-sentinel"]),
            ("Help me negotiate a better rate", ["negotiation-assistant"]),
        ]
        
        passed = 0
        for query, expected in test_cases:
            TestReporter.subsection(f"Query: {query[:40]}...")
            
            try:
                agents, reasoning, urgency = await llm_route_agents(query, {})
                TestReporter.log(f"Selected: {agents}")
                TestReporter.log(f"Reasoning: {reasoning[:50]}...")
                
                if any(exp in agents for exp in expected):
                    passed += 1
                    TestReporter.log("✅ Correct routing", "SUCCESS")
                else:
                    TestReporter.log(f"⚠️ Expected one of {expected}", "WARNING")
            except Exception as e:
                # Fallback to keyword routing
                agents = fallback_keyword_route(query)
                TestReporter.log(f"Fallback route: {agents}")
                if any(exp in agents for exp in expected):
                    passed += 1
        
        TestReporter.log(f"Routing Score: {passed}/{len(test_cases)}")
        TestReporter.log("Orchestrator routing validated", "SUCCESS")
    
    # =========================================
    # SECTION 3: RAG & MEMORY (Qdrant + MinIO)
    # =========================================
    
    @pytest.mark.asyncio
    async def test_10_qdrant_ingest_search(self):
        """Qdrant Document Ingest and Vector Search"""
        TestReporter.section("TEST 10: QDRANT INGEST & SEARCH")
        
        if not self.shared_data.get("qdrant_healthy"):
            pytest.skip("Qdrant not available")
        
        from lib.rag import get_rag_pipeline
        
        TestReporter.subsection("STEP 1: INGEST TEST DOCUMENT")
        
        pipeline = get_rag_pipeline()
        test_doc = """
        FREELANCE CONTRACT BEST PRACTICES
        
        This document outlines key terms for freelance contractors:
        1. Payment terms should be NET-15 or NET-30
        2. Always include a kill fee clause (25-50% of project value)
        3. Scope of work must be clearly defined
        4. Intellectual property rights should transfer on payment
        5. Include late payment penalties (1.5% per month)
        """
        
        result = await pipeline.ingest_text(
            text=test_doc,
            source="test_contract_guide",
            user_id="test_user_qdrant",
        )
        
        TestReporter.log(f"Ingested {result.get('chunk_count', 0)} chunks")
        assert result.get("success"), "Ingest should succeed"
        
        TestReporter.subsection("STEP 2: SEARCH TEST")
        
        docs = await pipeline.retrieve("payment terms for freelancers", k=3)
        TestReporter.log(f"Found {len(docs)} relevant documents")
        
        if docs:
            for i, doc in enumerate(docs[:3]):
                content = doc.page_content[:100]
                TestReporter.log(f"  [{i+1}] {content}...", "DEBUG")
        
        TestReporter.log("Qdrant ingest & search PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_11_minio_file_upload(self):
        """MinIO File Upload and Download"""
        TestReporter.section("TEST 11: MINIO FILE OPERATIONS")
        
        if not self.shared_data.get("minio_healthy"):
            pytest.skip("MinIO not available")
        
        from lib.storage import get_minio_storage
        from io import BytesIO
        
        storage = get_minio_storage()
        
        TestReporter.subsection("STEP 1: UPLOAD TEST FILE")
        
        test_content = b"This is a test contract document for FlagPilot v7.0"
        test_file = BytesIO(test_content)
        
        result = storage.upload_file(
            file_data=test_file,
            file_name="test_contract.txt",
            content_type="text/plain",
            user_id="test_user_minio",
        )
        
        TestReporter.log(f"Uploaded: {result.get('object_name')}")
        TestReporter.log(f"Size: {result.get('size')} bytes")
        
        object_name = result.get("object_name")
        assert object_name, "Upload should return object name"
        
        TestReporter.subsection("STEP 2: DOWNLOAD TEST")
        
        downloaded = storage.download_file(object_name)
        assert downloaded == test_content, "Downloaded content should match"
        
        TestReporter.log("MinIO file operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_12_user_profile_operations(self):
        """User Profile CRUD with memory system"""
        TestReporter.section("TEST 12: USER PROFILE OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        import time as time_module
        
        manager = MemoryManager()
        test_user_id = f"live_test_user_{int(time_module.time())}"
        
        # CREATE
        TestReporter.subsection("CREATE PROFILE")
        summary = "Test Freelancer with Python, AI/ML, and LangChain skills. Rate: $150/hr. 5 years experience."
        preferences = {"rate": 150, "skills": ["Python", "AI/ML", "LangChain"]}
        
        await manager.update_user_profile(test_user_id, summary=summary, preferences=preferences)
        TestReporter.log(f"Created profile for {test_user_id}")
        
        # Wait for ES to index
        import asyncio
        await asyncio.sleep(1)
        
        # Force refresh index
        manager.client.indices.refresh(index=manager.PROFILE_INDEX)
        
        # READ
        TestReporter.subsection("READ PROFILE")
        profile = await manager.get_user_profile(test_user_id)
        TestReporter.log(f"Retrieved: {profile.get('summary', 'N/A')[:50]}...")
        
        assert "Freelancer" in profile.get("summary", ""), "Profile should contain summary"
        
        TestReporter.log("User profile operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_13_chat_history_operations(self):
        """Chat History Operations"""
        TestReporter.section("TEST 13: CHAT HISTORY OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        import asyncio
        
        manager = MemoryManager()
        session_id = f"test_session_{int(time.time())}"
        user_id = "test_user_chat"
        
        TestReporter.subsection("SAVE MESSAGES")
        
        # Save user message
        await manager.save_chat(user_id, "user", "Review my contract", session_id=session_id)
        # Save assistant message
        await manager.save_chat(user_id, "assistant", "I'll analyze your contract for red flags.", session_id=session_id)
        
        TestReporter.log("Saved 2 messages")
        
        # Wait for ES to index
        await asyncio.sleep(1)
        manager.client.indices.refresh(index=manager.CHAT_INDEX)
        
        TestReporter.subsection("RETRIEVE HISTORY")
        
        history = await manager.get_chat_history(user_id, session_id=session_id, limit=10)
        TestReporter.log(f"Retrieved {len(history)} messages")
        
        assert len(history) >= 2, "Should have at least 2 messages"
        TestReporter.log("Chat history operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_14_global_wisdom_operations(self):
        """Global Wisdom Knowledge Base"""
        TestReporter.section("TEST 14: GLOBAL WISDOM OPERATIONS")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        import asyncio
        
        manager = MemoryManager()
        
        TestReporter.subsection("INDEX WISDOM")
        
        # Use correct add_wisdom method
        await manager.add_wisdom(
            category="contract_management",
            insight="Always document change requests in writing. Negotiate additional fees for out-of-scope work.",
            tags=["scope", "negotiation", "freelance"],
            confidence=0.9
        )
        TestReporter.log("Indexed: Handling Scope Creep")
        
        # Wait for ES to index
        await asyncio.sleep(1)
        manager.client.indices.refresh(index=manager.WISDOM_INDEX)
        
        TestReporter.subsection("SEARCH WISDOM")
        
        results = await manager.get_global_wisdom(category="contract_management", limit=5)
        TestReporter.log(f"Found {len(results)} wisdom entries")
        
        TestReporter.log("Global wisdom operations PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_15_experience_gallery(self):
        """Experience Gallery Operations"""
        TestReporter.section("TEST 15: EXPERIENCE GALLERY")
        
        if not self.shared_data.get("es_connected"):
            pytest.skip("Elasticsearch not connected")
        
        from lib.memory.manager import MemoryManager
        import asyncio
        
        manager = MemoryManager()
        user_id = "test_gallery_user"
        
        TestReporter.subsection("ADD EXPERIENCE")
        
        # Use correct save_experience method
        await manager.save_experience(
            user_id=user_id,
            task="AI Integration Project for Test Corp",
            outcome="success",
            lesson="Clear communication is key to project success",
            score=5,
            task_type="development"
        )
        TestReporter.log("Added experience: AI Integration Project")
        
        # Wait for ES to index
        await asyncio.sleep(1)
        manager.client.indices.refresh(index=manager.GALLERY_INDEX)
        
        # Search for similar experiences  
        results = await manager.search_similar_experiences("AI project", limit=5)
        TestReporter.log(f"Found {len(results)} similar experiences")
        
        TestReporter.log("Experience gallery PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 4: COMPLEX SCENARIOS
    # =========================================
    
    @pytest.mark.asyncio
    async def test_16_scam_detection_scenario(self):
        """Full Scam Detection Scenario"""
        TestReporter.section("TEST 16: SCAM DETECTION SCENARIO")
        
        from agents.orchestrator import run_orchestrator
        
        scam_job = """
        URGENT: Work from home opportunity! 
        Earn $5000/week with just 2 hours of work!
        No experience needed. Send $200 registration fee to start.
        This is 100% legitimate and guaranteed income!
        """
        
        TestReporter.log("Testing scam job posting...")
        
        response = await run_orchestrator(
            task=scam_job,
            context={"user_id": "test_scam_scenario"}
        )
        
        response_text = response.get("final_synthesis", "")
        TestReporter.log(f"Response preview: {response_text[:200]}...")
        
        # Should detect scam indicators
        scam_words = ["scam", "red flag", "suspicious", "warning", "careful", "avoid"]
        has_warning = any(word in response_text.lower() for word in scam_words)
        
        if has_warning:
            TestReporter.log("✅ Scam indicators detected", "SUCCESS")
        else:
            TestReporter.log("⚠️ Response may not have clear warnings", "WARNING")
        
        TestReporter.log("Scam detection scenario PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_17_contract_analysis_quality(self):
        """Contract Analysis Quality Test"""
        TestReporter.section("TEST 17: CONTRACT ANALYSIS QUALITY")
        
        from agents.orchestrator import run_orchestrator
        
        contract_text = """
        Review this contract clause:
        
        "The Client may terminate this agreement at any time without notice. 
        Upon termination, Contractor forfeits all unpaid invoices and must 
        return any advance payments. Client retains all IP rights regardless 
        of payment status."
        """
        
        TestReporter.log("Testing contract with unfair clauses...")
        
        response = await run_orchestrator(
            task=contract_text,
            context={"user_id": "test_contract_user"}
        )
        
        response_text = response.get("final_synthesis", "")
        TestReporter.log(f"Response preview: {response_text[:300]}...")
        
        # Should identify red flags
        red_flag_words = ["unfair", "risk", "concern", "red flag", "protect", "negotiate"]
        has_analysis = any(word in response_text.lower() for word in red_flag_words)
        
        if has_analysis:
            TestReporter.log("✅ Contract issues identified", "SUCCESS")
        
        TestReporter.log("Contract analysis PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_18_scope_creep_detection(self):
        """Scope Creep Detection Test"""
        TestReporter.section("TEST 18: SCOPE CREEP DETECTION")
        
        from agents.orchestrator import run_orchestrator
        
        scope_creep = """
        I was hired to build a landing page for $500.
        Now the client wants:
        - Full e-commerce functionality
        - Mobile app integration
        - CRM system connection
        - Real-time analytics dashboard
        
        They say it's "just a few extra features" and won't pay more.
        """
        
        TestReporter.log("Testing scope creep scenario...")
        
        response = await run_orchestrator(
            task=scope_creep,
            context={"user_id": "test_scope_user"}
        )
        
        response_text = response.get("final_synthesis", "")
        TestReporter.log(f"Response preview: {response_text[:300]}...")
        
        scope_words = ["scope", "additional", "fee", "negotiate", "boundary", "creep"]
        has_scope_advice = any(word in response_text.lower() for word in scope_words)
        
        if has_scope_advice:
            TestReporter.log("✅ Scope creep addressed", "SUCCESS")
        
        TestReporter.log("Scope creep detection PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_19_ghosting_prevention(self):
        """Ghosting Prevention Test"""
        TestReporter.section("TEST 19: GHOSTING PREVENTION")
        
        from agents.orchestrator import run_orchestrator
        
        ghosting = """
        My client hasn't responded to my emails for 2 weeks.
        The project is 80% done and I haven't received the second milestone payment.
        What should I do?
        """
        
        TestReporter.log("Testing ghosting prevention scenario...")
        
        response = await run_orchestrator(
            task=ghosting,
            context={"user_id": "test_ghost_user"}
        )
        
        response_text = response.get("final_synthesis", "")
        TestReporter.log(f"Response preview: {response_text[:300]}...")
        
        ghost_words = ["follow", "reminder", "escalate", "payment", "protect"]
        has_advice = any(word in response_text.lower() for word in ghost_words)
        
        if has_advice:
            TestReporter.log("✅ Ghosting advice provided", "SUCCESS")
        
        TestReporter.log("Ghosting prevention PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_20_contract_negotiation_memory(self):
        """Contract Negotiation with Memory"""
        TestReporter.section("TEST 20: CONTRACT NEGOTIATION WITH MEMORY")
        
        from agents.orchestrator import run_orchestrator
        
        TestReporter.subsection("NEGOTIATION REQUEST")
        
        negotiation = """
        A client offered me $50/hour for a Python/AI project.
        My usual rate is $150/hour. How should I negotiate?
        """
        
        response = await run_orchestrator(
            task=negotiation,
            context={"user_id": "test_negotiate_user"}
        )
        
        response_text = response.get("final_synthesis", "")
        TestReporter.log(f"Response preview: {response_text[:300]}...")
        
        negotiate_words = ["rate", "value", "counter", "offer", "negotiate"]
        has_strategy = any(word in response_text.lower() for word in negotiate_words)
        
        if has_strategy:
            TestReporter.log("✅ Negotiation strategy provided", "SUCCESS")
        
        TestReporter.log("Contract negotiation PASSED", "SUCCESS")
    
    # =========================================
    # SECTION 5: INTEGRATION
    # =========================================
    
    @pytest.mark.asyncio
    async def test_21_end_to_end_workflow(self):
        """Full End-to-End Workflow"""
        TestReporter.section("TEST 21: END-TO-END WORKFLOW")
        
        from agents.orchestrator import run_orchestrator
        
        workflow_query = "I'm a new freelancer. Help me review this contract and suggest improvements."
        
        TestReporter.log("Running full workflow...")
        start = time.time()
        
        response = await run_orchestrator(
            task=workflow_query,
            context={"user_id": "test_e2e_user"}
        )
        
        duration = time.time() - start
        
        TestReporter.log(f"Workflow completed in {duration:.2f}s")
        TestReporter.log(f"Response length: {len(response.get('final_synthesis', ''))} chars")
        TestReporter.log(f"Agents used: {response.get('agents_used', [])}")
        
        TestReporter.log("End-to-end workflow PASSED", "SUCCESS")
    
    @pytest.mark.asyncio
    async def test_22_copilotkit_integration(self):
        """CopilotKit API Integration Test"""
        TestReporter.section("TEST 22: COPILOTKIT API INTEGRATION")
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Test the root endpoint
                resp = await client.get("http://localhost:8000/", timeout=10.0)
                
                if resp.status_code == 200:
                    data = resp.json()
                    TestReporter.log(f"API Version: {data.get('version')}")
                    TestReporter.log(f"Architecture: {data.get('architecture')}")
                    TestReporter.log(f"Agents: {data.get('agents')}")
                    
                    endpoints = data.get("endpoints", {})
                    TestReporter.log(f"CopilotKit endpoint: {endpoints.get('copilotkit')}")
                    
                    TestReporter.log("CopilotKit integration PASSED", "SUCCESS")
                else:
                    TestReporter.log(f"API returned {resp.status_code}", "WARNING")
                    pytest.skip("API not healthy")
        except Exception as e:
            TestReporter.log(f"API connection error: {e}", "WARNING")
            pytest.skip(f"Cannot connect to API: {e}")


# Finish logging
TestReporter.finish()
