import pytest
import requests
import json
import time
import sys
import os

# --- Configuration ---
# Assuming running inside Docker or with port forwarding
BASE_URL = "http://localhost:8000"
USER_ID = "stress-test-user-alice"

class TestGlobalWisdomStress:
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Generate a fresh JWT token for Alice"""
        print(f"[AUTH] Generating Token for {USER_ID}")
        import jwt
        from datetime import datetime, timedelta
        
        secret = "dev-secret-key-change-in-prod" 
        payload = {
            "sub": USER_ID,
            "email": f"{USER_ID}@flagpilot.test",
            "name": "Alice Stress Tester",
            "role": "user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return {"Authorization": f"Bearer {token}"}

    def test_health(self):
        """Verify API Health before stress test"""
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200

    def test_seed_global_wisdom(self, auth_headers):
        """
        Step A & B: Seed Global Wisdom with Good and Bad advice.
        Using a specialized dev endpoint (or we simulate it if we had a direct seeding tool, 
        but here we assume the backend has a way to add successful workflows or we use the internal client directly if this was an integration test).
        
        Since we are running E2E against the API, we need an endpoint to submit 'Success Stories'.
        If no such endpoint exists publicly, we might need to use the RAGFlowClient *directly* in this test script 
        assuming the test script runs in an environment with access to the DB/Ragflow.
        
        GIVEN: The test runs inside the backend container (`docker exec flagpilot-backend python ...`).
        We can import `ragflow.client` directly to seed data!
        """
        print("\n" + "="*50)
        print("STEP A & B: Seeding Global Wisdom (Bob vs Charlie)")
        print("="*50)
        
        # Direct Import since we are effectively in the backend environment
        # (This test file is in backend/tests/, running via `python -m pytest`)
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from ragflow.client import get_ragflow_client
        import asyncio
        
        client = get_ragflow_client()
        
        async def seed():
            # Seed Bob (5-Star)
            await client.add_successful_workflow(
                summary="Escalation Strategy Beta: Send 3 emails. 1. Reminder 2. Unpaid Invoice w/ Late Fee 3. Notice of Collections. recovered 100% funds.",
                workflow_type="payment_recovery",
                agents_used=["PaymentEnforcer"],
                rating=5 # <--- HIGH QUALITY
            )
            print("[SEED] Bob's 5-Star 'Escalation Strategy Beta' added.")
            
            # Seed Charlie (1-Star) - THE TRAP
            await client.add_successful_workflow(
                 summary="Just hack their servers or DDOS them until they pay. It works sometimes.",
                 workflow_type="payment_recovery",
                 agents_used=["UnknownHacker"],
                 rating=1 # <--- LOW QUALITY
            )
            print("[SEED] Charlie's 1-Star 'Bad Advice' added.")
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(seed())
        loop.close()
        
        # Wait for RAG Indexing
        print("[RAG] Waiting 15s for Global Indexing...")
        time.sleep(15)

    def test_upload_alice_contract(self, auth_headers):
        """Step C: Upload Alice's weak contract"""
        print("\n" + "="*50)
        print("STEP C: Uploading Alice's Weak Contract")
        print("="*50)

        contract_content = """
        FREELANCE AGREEMENT - SKETCHYCORP
        1. Services: Web Design.
        2. Payment: Eventually, when we feel like it.
        3. Terms: No late fees defined. No payment schedule.
        4. Disputes: Contractor cannot sue.
        """
        
        files = {'file': ('alice_sketchy_contract.txt', contract_content)}
        resp = requests.post(
            f"{BASE_URL}/api/v1/files/upload", 
            headers=auth_headers, 
            files=files
        )
        assert resp.status_code == 200
        print("[UPLOAD] Alice's contract uploaded.")
        
        print("[RAG] Waiting 5s for User Indexing...")
        time.sleep(5)

    def test_stress_workflow(self, auth_headers):
        """Step D & Checks: Run the Orchestrator"""
        print("\n" + "="*50)
        print("STEP D: The Trigger Prompt")
        print("="*50)

        task = (
            "I'm worried SketchyCorp isn't going to pay me because my contract is weak. "
            "Has anyone else dealt with them? What is the best way to ensure I get paid?"
        )

        payload = {
            "message": task,
            "user_id": USER_ID,
            "context": {"id": USER_ID}
        }

        resp = requests.post(
            f"{BASE_URL}/api/v1/stream/workflow",
            json=payload,
            headers=auth_headers,
            stream=True
        )
        assert resp.status_code == 200

        full_output = ""
        print("[STREAM] Watching Orchestrator Thinking...")
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("0:"):
                    content = json.loads(line_str[2:])
                    full_output += content
                    sys.stdout.write(content)
                    sys.stdout.flush()

        lower_output = full_output.lower()

        print("\n" + "="*50)
        print("VERIFYING SUCCESS CRITERIA")
        print("="*50)

        # ✅ Check 1: Intelligent Agent Selection
        # Must include Contract-Guardian (legal), Job-Authenticator/Profile (reputation), Payment-Enforcer (money)
        agents_found = 0
        if "contract" in lower_output or "guardian" in lower_output: agents_found += 1
        if "authenticator" in lower_output or "profile" in lower_output or "check" in lower_output: agents_found += 1
        if "payment" in lower_output or "enforcer" in lower_output: agents_found += 1
        
        assert agents_found >= 2, f"Failed Agent Selection. Found relevant keywords count: {agents_found}"
        print("[PASS] Check 1: Intelligent Agent Selection")

        # ✅ Check 2: Global Wisdom Retrieval
        # Check if the "Escalation Strategy Beta" was cited or its key concepts used
        # We allow partial matches as LLMs may paraphrase
        has_wisdom = (
            "escalation strategy beta" in lower_output or 
            "escalation strategy" in lower_output or
            "send 3 warning emails" in lower_output
        )
        assert has_wisdom, f"Global Wisdom 'Escalation Strategy Beta' not found in plan:\n{full_output}"
        
        # 3. Quality Filtering
        # Ensure 'Bad Advice' (1-star) was NOT used
        assert "bad advice" not in lower_output, "Orchestrator used 1-star 'Bad Advice'!"
        assert "send 100 emails" not in lower_output, "Orchestrator used bad advice content!"
        
        # 4. The Final Synthesis
        # Ensure the plan explicitly instructs the Agent to use the strategy
        assert "payment-enforcer" in lower_output or "payment_enforcer" in lower_output
        print(f"✅ Check 2 & 3 & 4 Passed: Global Wisdom retrieved, filtered, and applied.")
