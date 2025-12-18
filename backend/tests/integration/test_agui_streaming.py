import pytest
from fastapi.testclient import TestClient
from main import app
import json
import uuid

client = TestClient(app)

@pytest.mark.live
def test_agui_streaming_format():
    """Test that the /api/team/chat endpoint returns valid AG-UI SSE stream"""
    run_id = str(uuid.uuid4())
    payload = {
        "thread_id": str(uuid.uuid4()),
        "run_id": run_id,
        "messages": [
            {"id": str(uuid.uuid4()), "role": "user", "content": "Hello, who are you?"}
        ],
        "agents": ["job-authenticator"] # Use a valid agent
    }
    
    with client.stream("POST", "/api/team/chat", json=payload) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        events = []
        for line in response.iter_lines():
            if line:
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    events.append(data)
                    if len(events) > 20: 
                        break
        
        # Verify event sequence and structure
        assert len(events) > 0
        
        # 1. First event should be RUN_STARTED
        assert events[0]["type"] == "RUN_STARTED"
        assert events[0]["runId"] == run_id
        
        # 2. Should have a STATE_SNAPSHOT
        assert any(e["type"] == "STATE_SNAPSHOT" for e in events)
        
        # 3. Should have STEP_STARTED
        assert any(e["type"] == "STEP_STARTED" for e in events)
        
        # Verify camelCase conversion
        for e in events:
            # Check that common snake_case keys are now camelCase
            assert "run_id" not in e or e["type"] == "RUN_STARTED" # run_id is allowed in some but we want to see runId
            # Actually our encoder converts EVERYTHING to camelCase
            if "runId" in e:
                assert "run_id" not in e

@pytest.mark.live
def test_agent_state_endpoint():
    """Test the production state endpoint"""
    # Trigger a run first if possible, or just check the endpoint returns something
    response = client.get("/api/agents/sentinel/state")
    assert response.status_code == 200
    data = response.json()
    assert "agentId" in data
    assert "state" in data

@pytest.mark.live
def test_stop_run_endpoint():
    """Test the run cancellation endpoint"""
    # Try stopping a non-existent run
    response = client.post("/api/runs/non-existent-id/stop")
    assert response.status_code == 404
