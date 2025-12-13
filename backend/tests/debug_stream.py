"""
Backend Debug Test Script
Tests the /api/v1/stream/workflow endpoint and prints all responses verbosely.
"""

import asyncio
import httpx
import json
from typing import AsyncGenerator

BACKEND_URL = "http://127.0.0.1:8000"

async def test_workflow_stream():
    """Test the workflow streaming endpoint"""
    print("=" * 60)
    print("BACKEND STREAMING DEBUG TEST")
    print("=" * 60)
    print(f"URL: {BACKEND_URL}/api/v1/stream/workflow")
    print()
    
    payload = {
        "message": "Hello, what can you help me with?",
        "context": {},
        "user_id": "test-debug-user"
    }
    
    print(f"Request Payload: {json.dumps(payload, indent=2)}")
    print()
    print("-" * 60)
    print("STREAMING RESPONSE:")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{BACKEND_URL}/api/v1/stream/workflow",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print()
                
                if response.status_code != 200:
                    body = await response.aread()
                    print(f"ERROR Response Body: {body.decode()}")
                    return
                
                print("--- STREAM START ---")
                line_count = 0
                async for line in response.aiter_lines():
                    line_count += 1
                    print(f"[{line_count:03d}] RAW: {repr(line)}")
                    
                    # Parse Vercel AI SDK format
                    if line and len(line) > 2 and line[1] == ":":
                        code = line[0]
                        content = line[2:]
                        
                        if code == "0":
                            # Text content
                            try:
                                text = json.loads(content)
                                print(f"      -> TEXT: {text}")
                            except:
                                print(f"      -> TEXT (raw): {content}")
                        
                        elif code == "2":
                            # Data event
                            try:
                                data = json.loads(content)
                                print(f"      -> DATA: {json.dumps(data, indent=8)}")
                            except:
                                print(f"      -> DATA (raw): {content}")
                        
                        elif code == "3":
                            # Error
                            print(f"      -> ERROR: {content}")
                        
                        elif code == "d":
                            # Finish
                            try:
                                finish = json.loads(content)
                                print(f"      -> FINISH: {finish}")
                            except:
                                print(f"      -> FINISH (raw): {content}")
                        
                        else:
                            print(f"      -> CODE {code}: {content}")
                    
                print("--- STREAM END ---")
                print(f"Total lines received: {line_count}")
                
    except httpx.ConnectError as e:
        print(f"\n❌ CONNECTION ERROR: Cannot connect to backend at {BACKEND_URL}")
        print(f"   Error: {e}")
        print("\n   Make sure the backend is running with:")
        print("   cd backend && python run.py")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")

async def test_health():
    """Test if backend is reachable"""
    print("Checking backend health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/health")
            print(f"Health check: {response.status_code} - {response.text}")
            return response.status_code == 200
    except httpx.ConnectError:
        print(f"❌ Backend not reachable at {BACKEND_URL}")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def main():
    print("\n" + "=" * 60)
    print("FLAGPILOT BACKEND DEBUG TEST")
    print("=" * 60 + "\n")
    
    # Step 1: Health check
    is_healthy = await test_health()
    print()
    
    if not is_healthy:
        print("⚠️  Backend is not running!")
        print("    Please start it with:")
        print("    cd backend && python run.py")
        return
    
    # Step 2: Test streaming
    await test_workflow_stream()
    
    print("\n" + "=" * 60)
    print("DEBUG TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
