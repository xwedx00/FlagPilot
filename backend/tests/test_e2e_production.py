import pytest
import requests
import json
import time
import sys
import os

# --- Configuration ---
BASE_URL = "http://localhost:8000"
USER_ID = "production-test-user-v1"
TEST_FILES = {
    "job_description.txt": """
    JOB DESCRIPTION: SENIOR PYTHON BACKEND ENGINEER
    - Must have 5+ years of Python experience.
    - Expertise in FastAPI, Docker, and AWS.
    - Role is 100% Remote.
    - Salary Range: $160,000 - $200,000.
    """,
    "resume_senior.txt": """
    RESUME: Sarah Architect
    - 8 years experience in Python & Go.
    - Built scalable microservices using FastAPI and Kubernetes on AWS.
    - Seeking Remote role.
    - Current Salary: $180k. Expecting $190k+.
    """,
    "standard_contract.txt": """
    STANDARD EMPLOYMENT AGREEMENT (TEMPLATE)
    1. PROBATION: 3 months.
    2. IP RIGHTS: All code belongs to company.
    3. NON-COMPETE: 12 months post-employment.
    4. EQUIPMENT: Company provided laptop.
    5. LOCATION: Employee must reside in US.
    """
}

class TestProductionE2E:
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Generate a fresh JWT token for the test user"""
        print(f"[AUTH] Generating Token for {USER_ID}")
        # Assuming dev mode allows auto-creation or using a test endpoint if available.
        # Fallback to stub if needed, but project uses verified JWT now.
        # Ideally we use an endpoint to get a token. 
        # For this cleanup, we will assume we can generate a valid self-signed token if the secret is known (dev-secret-key-change-in-prod)
        import jwt
        from datetime import datetime, timedelta
        
        secret = "dev-secret-key-change-in-prod" # Matched from config.py
        payload = {
            "sub": USER_ID,
            "email": f"{USER_ID}@flagpilot.test",
            "name": "Production Test User",
            "role": "user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return {"Authorization": f"Bearer {token}"}

    def test_health(self):
        """Verify API Health"""
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "agents" in data

    def test_upload_documents(self, auth_headers):
        """Step 1: Upload Recruitment Documents"""
        print("\n" + "="*50)
        print("STEP 1: Uploading Documents")
        print("="*50)

        for filename, content in TEST_FILES.items():
            files = {'file': (filename, content)}
            resp = requests.post(
                f"{BASE_URL}/api/v1/files/upload", 
                headers=auth_headers, 
                files=files
            )
            if resp.status_code != 200:
                print(f"[ERROR] Upload failed for {filename}: {resp.text}")
            assert resp.status_code == 200
            print(f"[UPLOAD] {filename} success.")
        
        # Give RAG time to index
        print("[RAG] Wating 5s for indexing...")
        time.sleep(5)

    def test_full_workflow(self, auth_headers):
        """Step 2: Execute Complex Workflow"""
        print("\n" + "="*50)
        print("STEP 2: Executing Workflow")
        print("="*50)

        task = (
            "1. Analyze the 'Sarah' resume against the Job Description. "
            "2. Then, analyze the 'Standard Employment Agreement' specifically for her. "
            "Are there any risks regarding the Non-Compete clause?"
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
        print("[STREAM] Streaming response...")
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("0:"):
                    content = json.loads(line_str[2:])
                    full_output += content
                    sys.stdout.write(content)
                    sys.stdout.flush()

        lower_output = full_output.lower()
        
        # Assertions
        assert "sarah" in lower_output, "Agent failed to identify Sarah"
        assert "non-compete" in lower_output, "Agent failed to identify Non-Compete risk"
        print("\n[SUCCESS] Workflow Verified.")
