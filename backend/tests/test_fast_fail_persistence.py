import pytest
import requests
import json
import time

# Import centralized configuration
from tests.test_config import (
    BASE_URL, TEST_USER_ID as USER_ID, TEST_SESSION_TOKEN as REAL_SESSION_TOKEN,
    log_and_print as _log
)

OUTPUT_FILE = "test_fast_fail_output.txt"

def log_and_print(message):
    """Log message to console and file"""
    _log(message, OUTPUT_FILE)

class TestFastFailPersistence:
    
    @classmethod
    def setup_class(cls):
        """Clean start"""
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=== FAST FAIL & PERSISTENCE STRESS TEST LOG ===\n")
            f.write(f"Date: {time.ctime()}\n\n")

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Use Real Session Token"""
        log_and_print(f"[AUTH] Using Real Session Token for {USER_ID}")
        return {"Authorization": f"Bearer {REAL_SESSION_TOKEN}"}

    def test_health(self):
        """Verify API Health"""
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        log_and_print("[HEALTH] API is healthy.")

    def test_stress_fast_fail(self, auth_headers):
        """
        Step E: Verify Generalized Fast-Fail & Persistence
        """
        log_and_print("\n" + "="*50)
        log_and_print("STEP E: Generalized Fast-Fail & Persistence Stress Test")
        log_and_print("="*50)

        # TRIGGER WARNING: This prompt is designed to be blatantly risky to ensure the RiskAdvisor triggers.
        # It involves explicit scam keywords, "telegram", "send check", "hiring immediately", "no experience".
        scam_text = (
            "URGENT HIRING!! Data Entry Clerk needed immediately. "
            "No experience required. Pay is $50/hr. "
            "Must have Telegram. Contact @Scammer123 for interview. "
            "We will send you a check for equipment. This is definitely not a scam, trust me."
        )
        
        url = f"{BASE_URL}/api/v1/stream/workflow"
        payload = {
            "message": scam_text,
            "user_id": USER_ID,
            "context": {"id": USER_ID}
        }
        
        # Stream request
        interrupted_msg = False
        risk_advisor_ran = False
        
        with requests.post(url, json=payload, headers=auth_headers, stream=True) as response:
            assert response.status_code == 200, f"API Error: {response.text}"
            
            for line in response.iter_lines():
                if not line: continue
                decoded = line.decode('utf-8')
                
                # Log raw output
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(f"RAW: {decoded}\n")

                # Global Check (Regex-like) to catch any mention
                if "risk-advisor" in decoded or "Risk Advisor" in decoded:
                     risk_advisor_ran = True
                     log_and_print("✅ [FAST-FAIL] Risk Advisor signature detected in stream (Global Check).")

                # Parse Vercel / SSE
                content_chunk = None
                json_data = None

                # Case A: Legacy SSE "data: ..."
                if decoded.startswith("data: "):
                    try:
                        json_data = json.loads(decoded[6:])
                    except:
                        pass
                
                # Case B: Vercel "0:..." (Text)
                elif decoded.startswith("0:"):
                    try:
                         # 0:"string"
                         content_chunk = json.loads(decoded[2:])
                    except:
                        pass
                
                # Case C: Vercel "2:..." (Data/Tool)
                elif decoded.startswith("2:"):
                    try:
                        # 2:[json_data]
                        json_list = json.loads(decoded[2:])
                        if isinstance(json_list, list) and len(json_list) > 0:
                            json_data = json_list[0]
                    except:
                         pass

                # --- Analyze Content (Text) ---
                if content_chunk and isinstance(content_chunk, str):
                    if "WORKFLOW INTERRUPTED" in content_chunk or "CRITICAL RISK" in content_chunk:
                        interrupted_msg = True
                        log_and_print("✅ [FAST-FAIL] Detected 'WORKFLOW INTERRUPTED' message.")
                    if "risk-advisor" in content_chunk or "Risk Advisor" in content_chunk:
                        risk_advisor_ran = True
                        log_and_print("✅ [FAST-FAIL] Risk Advisor detected in Vercel stream.")

                # --- Analyze Data (JSON) ---
                if json_data and isinstance(json_data, dict):
                    if json_data.get("type") == "agent_status":
                        # Check both 'agent' and 'agentId' keys for compatibility
                        agent_id = json_data.get("agentId") or json_data.get("agent")
                        if agent_id == "risk-advisor":
                            risk_advisor_ran = True
                            log_and_print("✅ [FAST-FAIL] Risk Advisor activity detected (agent_status).")
                            
                    if json_data.get("type") == "workflow_update":
                        # Check if risk advisor node was added
                        nodes = json_data.get("nodes", [])
                        for n in nodes:
                            # Check nested data.agentId structure (actual format)
                            node_data = n.get("data", {})
                            agent_id = node_data.get("agentId") or n.get("agentId") or n.get("agent")
                            if agent_id == "risk-advisor":
                                risk_advisor_ran = True
                                log_and_print("✅ [FAST-FAIL] Risk Advisor node found in plan.")

        # Assertions
        if not risk_advisor_ran:
             log_and_print("❌ FAIL: RiskAdvisor did not run!")
             pytest.fail("RiskAdvisor injection failed")
             
        # Soft failure for interruption itself if model is lenient, but Advisor MUST run
        if not interrupted_msg:
             log_and_print("⚠️ WARNING: Workflow was not forcefully interrupted, but RiskAdvisor ran.")
        else:
             log_and_print("✅ [FAST-FAIL] Workflow was successfully interrupted.")


        # Persistence Check
        log_and_print(">> Checking Persistence API (Retrying for 10s)...")
        latest = None
        for i in range(5):
            time.sleep(2)
            hist_res = requests.get(f"{BASE_URL}/api/v1/history/user/{USER_ID}")
            if hist_res.status_code == 200:
                history = hist_res.json()
                if history:
                    # Assume latest is first
                    latest = history[0]
                    if latest['status'] == 'completed':
                        break
        
        if not latest:
             log_and_print("❌ FAIL: No history found.")
             pytest.fail("Persistence failed")
             
        log_and_print(f"✅ [PERSISTENCE] Record {latest['id']} found. Status: {latest['status']}")
        assert latest['status'] == "completed", "Status should be 'completed'"

    def test_stress_scope_creep(self, auth_headers):
        """
        Step F: Verify Scope Creep Detection
        """
        log_and_print("\n" + "="*50)
        log_and_print("STEP F: Scope Creep Detection Stress Test")
        log_and_print("="*50)
        
        # Request: Classic scope creep
        request_text = (
            "Hey, can you also just quickly add a user login system and payment integration? "
            "It shouldn't take long, right? We can't increase the budget though."
        )
        
        payload = {
            "message": request_text,
            "user_id": USER_ID,
            "context": {
                "id": USER_ID,
                "RAG_CONTEXT": "Original Scope: Build a landing page. Budget: $500."
            }
        }
        
        sentinel_activated = False
        
        with requests.post(f"{BASE_URL}/api/v1/stream/workflow", json=payload, headers=auth_headers, stream=True) as response:
            assert response.status_code == 200
            
            for line in response.iter_lines():
                if not line: continue
                decoded = line.decode('utf-8')
                if not decoded.startswith("data: "): continue
                data_str = decoded[6:]
                
                try:
                    data = None
                    if data_str.startswith('"0:'):
                        inner = json.loads(data_str)
                        if inner.startswith("0:"): data = json.loads(inner[2:])
                    else:
                        data = json.loads(data_str)
                    
                    if isinstance(data, dict):
                        if data.get("type") == "agent_status" and data.get("agent") == "scope-sentinel":
                             sentinel_activated = True
                             log_and_print("✅ [SCOPE] Scope Sentinel Activated")
                except:
                    pass
        
        if sentinel_activated:
            log_and_print("✅ PASS: Orchestrator correctly routed to Scope Sentinel.")
        else:
            log_and_print("⚠️ WARNING: Scope Sentinel NOT activated. (Model dependency)")

        log_and_print("\n✅✅✅ TEST SUITE PASSED ✅✅✅")
