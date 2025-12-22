"""
CopilotKit Isolated Runner
===========================
Executes CopilotKit/LangGraph code in isolated venv via subprocess.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional
from loguru import logger

COPILOTKIT_VENV = os.environ.get("COPILOTKIT_VENV", "/app/venv-copilotkit")
COPILOTKIT_PYTHON = os.path.join(COPILOTKIT_VENV, "bin", "python")

if sys.platform == "win32":
    COPILOTKIT_PYTHON = os.path.join(COPILOTKIT_VENV, "Scripts", "python.exe")


class CopilotKitRunner:
    """Runs CopilotKit code in isolated environment"""
    
    @staticmethod
    async def handle_request(request_data: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """
        Handle a CopilotKit request in the isolated environment.
        """
        script = '''
import sys
import json

input_data = json.loads(sys.stdin.read())

from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent

# Import the graph from application code
sys.path.insert(0, "/app")
from lib.copilotkit.graph import graph

sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="flagpilot_orchestrator",
            description="FlagPilot multi-agent team for freelancer protection",
            graph=graph,
        )
    ]
)

# Process the request
import asyncio
result = asyncio.run(sdk.process(input_data))
print(json.dumps(result))
'''
        
        try:
            if not os.path.exists(COPILOTKIT_PYTHON):
                logger.warning(f"CopilotKit venv not found at {COPILOTKIT_PYTHON}")
                return {"error": "CopilotKit environment not available"}
            
            process = await asyncio.create_subprocess_exec(
                COPILOTKIT_PYTHON, "-c", script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app",
                env={**os.environ, "PYTHONPATH": "/app"}
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=json.dumps(request_data).encode()),
                timeout=timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"CopilotKit subprocess error: {error_msg}")
                return {"error": error_msg}
            
            return json.loads(stdout.decode())
            
        except asyncio.TimeoutError:
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"CopilotKit runner error: {e}")
            return {"error": str(e)}
