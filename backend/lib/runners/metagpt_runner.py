"""
MetaGPT Isolated Runner
========================
Executes MetaGPT agents in isolated venv via subprocess.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, List
from loguru import logger

METAGPT_VENV = os.environ.get("METAGPT_VENV", "/app/venv-metagpt")
METAGPT_PYTHON = os.path.join(METAGPT_VENV, "bin", "python")

if sys.platform == "win32":
    METAGPT_PYTHON = os.path.join(METAGPT_VENV, "Scripts", "python.exe")


class MetaGPTRunner:
    """Runs MetaGPT agents in isolated environment"""
    
    @staticmethod
    async def run_team(
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run FlagPilotTeam in the isolated MetaGPT environment.
        """
        input_data = {
            "task": task,
            "context": context or {},
            "agents": agents
        }
        
        script = '''
import sys
import json
import asyncio
import os

# Set environment for MetaGPT
sys.path.insert(0, "/app")
os.chdir("/app")

# Configure MetaGPT environment
from config import settings
settings.configure_metagpt_env()

# Apply patches
from lib.patches import apply_metagpt_patches
apply_metagpt_patches()

input_data = json.loads(sys.stdin.read())

async def main():
    from agents.team import FlagPilotTeam
    
    team = FlagPilotTeam(agents=input_data.get("agents"))
    result = await team.run(
        task=input_data["task"],
        context=input_data.get("context", {})
    )
    
    output = {
        "task": result.get("task", ""),
        "agent_outputs": {k: str(v) for k, v in result.get("agent_outputs", {}).items()},
        "final_synthesis": str(result.get("final_synthesis", "")),
        "status": result.get("status", "COMPLETED"),
        "risk_level": result.get("risk_level", "none"),
        "error": result.get("error")
    }
    
    print(json.dumps(output))

asyncio.run(main())
'''
        
        try:
            if not os.path.exists(METAGPT_PYTHON):
                logger.warning(f"MetaGPT venv not found at {METAGPT_PYTHON}, using fallback")
                return await MetaGPTRunner._run_fallback(task, context, agents)
            
            process = await asyncio.create_subprocess_exec(
                METAGPT_PYTHON, "-c", script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app",
                env={**os.environ, "PYTHONPATH": "/app"}
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=json.dumps(input_data).encode()),
                timeout=timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"MetaGPT subprocess error: {error_msg}")
                return {
                    "task": task,
                    "agent_outputs": {},
                    "final_synthesis": f"Error: {error_msg}",
                    "status": "ERROR",
                    "error": error_msg
                }
            
            return json.loads(stdout.decode())
            
        except asyncio.TimeoutError:
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": "Analysis timed out",
                "status": "TIMEOUT",
                "error": "Execution timeout"
            }
        except Exception as e:
            logger.error(f"MetaGPT runner error: {e}")
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": f"Error: {str(e)}",
                "status": "ERROR",
                "error": str(e)
            }
    
    @staticmethod
    async def _run_fallback(
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fallback when venv not available (dev mode)"""
        try:
            from agents.team import FlagPilotTeam
            team = FlagPilotTeam(agents=agents)
            result = await team.run(task=task, context=context or {})
            return {
                "task": result.get("task", ""),
                "agent_outputs": {k: str(v) for k, v in result.get("agent_outputs", {}).items()},
                "final_synthesis": str(result.get("final_synthesis", "")),
                "status": result.get("status", "COMPLETED"),
                "risk_level": result.get("risk_level", "none"),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": f"Error: {str(e)}",
                "status": "ERROR",
                "error": str(e)
            }
