
import pytest
import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000"
# Use a distinct user ID for isolation
USER_ID = f"test-user-{uuid4().hex[:8]}"

class TestFastFailAndPersistence:
    
    def test_generalized_fast_fail(self):
        """
        Verify that a clear scam triggers Generalized Fast-Fail:
        1. 'WORKFLOW INTERRUPTED' message.
        2. 'risk-advisor' is injected and runs.
        3. Workflow completes (handled by advisor).
        4. Persistence record shows 'completed'.
        """
        scam_text = (
            "URGENT HIRING!! Data Entry Clerk needed immediately. "
            "No experience required. Pay is $50/hr. "
            "Must have Telegram. Contact @Scammer123 for interview. "
            "We will send you a check for equipment."
        )
        
        url = f"{BASE_URL}/api/v1/stream/workflow"
        headers = {"Content-Type": "application/json"}
        payload = {
            "message": scam_text,
            "user_id": USER_ID,
            "context": {"id": USER_ID}
        }
        
        print(f"\n🚀 Sending Scam Job Test for User {USER_ID}...")
        
        # Stream request
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            assert response.status_code == 200, f"API Error: {response.text}"
            
            full_output = []
            interrupted_msg = False
            risk_advisor_ran = False
            execution_id = None
            
            # Manual SSE Parsing
            for line in response.iter_lines():
                if not line:
                    continue
                
                decoded_line = line.decode('utf-8')
                if not decoded_line.startswith("data: "):
                    continue
                    
                data_str = decoded_line[6:] # Strip "data: "
                
                # Check Vercel/Text format
                if data_str.startswith('"0:'):
                    # It's a string encoding JSON usually, or just text
                    # "0:\"...\""
                    try:
                        inner = json.loads(data_str)
                        if inner.startswith("0:"):
                             content = json.loads(inner[2:])
                             if "WORKFLOW INTERRUPTED" in content:
                                 interrupted_msg = True
                                 print("✅ Detected 'WORKFLOW INTERRUPTED' message.")
                             if "Persistence: Execution ID" in content:
                                 # Extract ID roughly or just note it
                                 print("✅ Persistence ID log found.")
                    except:
                        pass
                
                # Check Standard JSON format
                else:
                    try:
                        data = json.loads(data_str)
                        # print(f"DEBUG Event: {data}") # Uncomment for deeper debug
                        
                        # Check system messages/agent status
                        if data.get("type") == "agent_status":
                            if data.get("agent") == "risk-advisor":
                                risk_advisor_ran = True
                                print("✅ Risk Advisor active.")
                                
                        if data.get("type") == "message":
                             # Relaxed check for interrupt
                             if "INTERRUPTED" in data.get("content", "") or "CRITICAL" in data.get("content", ""):
                                 interrupted_msg = True
                                 print("✅ Detected Interrupt/Critical message.")

                    except:
                        pass
                        
        # ASSERTIONS
        if not interrupted_msg:
            print("❌ Start of Output Dump for Debugging:")
            print("\n".join(str(o) for o in full_output))
            print("❌ End of Output Dump")
        
        assert interrupted_msg, "Did not receive 'WORKFLOW INTERRUPTED' message."
        assert risk_advisor_ran, "Risk Advisor did not run."
        
        print("\n🔎 Verifying Persistence in History API...")
        
        # Retry logic for DB consistency (Async commits can be slow)
        latest_status = "unknown"
        for i in range(5):
            time.sleep(2) 
            hist_res = requests.get(f"{BASE_URL}/api/v1/history/user/{USER_ID}")
            if hist_res.status_code == 200:
                history = hist_res.json()
                if history:
                    latest = history[0]
                    latest_status = latest['status']
                    if latest_status == "completed":
                        break
        
        print(f"✅ History Record Found: {latest['id']}")
        print(f"   Status: {latest_status}")
        
        assert latest_status == "completed", f"Status is {latest_status}, expected 'completed'."
        
        print("✅ Test Passed!")

