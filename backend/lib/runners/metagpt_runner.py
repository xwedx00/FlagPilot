"""
MetaGPT Isolated Runner
========================
Executes MetaGPT FlagPilotTeam in isolated venv via subprocess.
Uses proper MetaGPT config2.yaml configuration for OpenRouter integration.
"""

import asyncio
import json
import os
import sys
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

METAGPT_VENV = os.environ.get("METAGPT_VENV", "/app/venv-metagpt")
METAGPT_PYTHON = os.path.join(METAGPT_VENV, "bin", "python")

if sys.platform == "win32":
    METAGPT_PYTHON = os.path.join(METAGPT_VENV, "Scripts", "python.exe")


def _create_metagpt_config(api_key: str, model: str, base_url: str) -> str:
    """Generate MetaGPT config2.yaml content"""
    # Use api_type="openai" for OpenRouter compatibility as "openrouter" enum 
    # is not in installed metagpt version
    return f"""# MetaGPT OpenRouter Configuration
llm:
  api_type: "openai"
  base_url: "{base_url}"
  api_key: "{api_key}"
  model: "{model}"
  timeout: 300
  max_token: 4096
  temperature: 0.3
  stream: false

repair_llm_output: true

search:
  api_type: "google" 
  api_key: "placeholder"
  cse_id: "placeholder"
"""


class MetaGPTRunner:
    """Runs MetaGPT FlagPilotTeam in isolated environment"""
    
    @staticmethod
    async def run_team(
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run FlagPilotTeam in the isolated MetaGPT environment.
        
        Creates proper config2.yaml before execution to ensure
        MetaGPT uses OpenRouter correctly.
        """
        from config import settings
        
        # Create config2.yaml in ~/.metagpt/ BEFORE running subprocess
        config_content = _create_metagpt_config(
            settings.OPENROUTER_API_KEY,
            settings.OPENROUTER_MODEL,
            settings.OPENROUTER_BASE_URL
        )
        
        # Write to /root/.metagpt/config2.yaml (where MetaGPT looks)
        metagpt_config_dir = Path("/root/.metagpt")
        metagpt_config_dir.mkdir(parents=True, exist_ok=True)
        config_path = metagpt_config_dir / "config2.yaml"
        config_path.write_text(config_content)
        
        logger.info(f"Created MetaGPT config at {config_path}")
        
        input_data = {
            "task": task,
            "context": context or {},
            "agents": agents,
        }
        
        # Script that runs FlagPilotTeam with proper config loading
        # MetaGPT will now find the config2.yaml we created
        script = '''
import sys
import json
import asyncio
import os
import warnings
import logging

# Suppress all logging to stderr
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

try:
    from loguru import logger
    logger.remove()
except:
    pass

warnings.filterwarnings("ignore")

# Set paths
sys.path.insert(0, "/app")
os.chdir("/app")
os.environ["METAGPT_PROJECT_ROOT"] = "/app"

# Read input
input_data = json.loads(sys.stdin.read())

async def main():
    output = None
    try:
        # Import FlagPilotTeam - MetaGPT will load config from ~/.metagpt/config2.yaml
        from agents.team import FlagPilotTeam
        
        task = input_data["task"]
        context = input_data.get("context", {})
        agents_list = input_data.get("agents")
        
        # Create and run team
        team = FlagPilotTeam(agents=agents_list)
        result = await team.run(task=task, context=context)
        
        # Format output
        output = {
            "task": result.get("task", task),
            "agent_outputs": {},
            "final_synthesis": str(result.get("final_synthesis", "")),
            "status": result.get("status", "COMPLETED"),
            "risk_level": result.get("risk_level", "UNKNOWN"),
            "error": result.get("error")
        }
        
        # Convert agent outputs
        for k, v in result.get("agent_outputs", {}).items():
            output["agent_outputs"][k] = str(v)[:4000]  # Increased limit for verbosity
            
        # Determine risk level
        combined = (output["final_synthesis"] + str(output["agent_outputs"])).lower()
        if any(w in combined for w in ["scam", "fraud", "money laundering", "illegal", "critical"]):
            output["risk_level"] = "HIGH"
        elif any(w in combined for w in ["warning", "caution", "concern", "red flag"]):
            output["risk_level"] = "MEDIUM"
        else:
            output["risk_level"] = "LOW"
            
    except Exception as e:
        import traceback
        output = {
            "task": input_data.get("task", ""),
            "agent_outputs": {},
            "final_synthesis": f"Team execution error: {str(e)}",
            "status": "ERROR",
            "risk_level": "UNKNOWN",
            "error": traceback.format_exc()
        }
    
    # Output JSON with delimiters for reliable parsing
    print(f"<<<JSON_START>>>{json.dumps(output)}<<<JSON_END>>>", flush=True)

asyncio.run(main())
'''
        
        try:
            if not os.path.exists(METAGPT_PYTHON):
                logger.warning(f"MetaGPT venv not found at {METAGPT_PYTHON}, using fallback")
                return await MetaGPTRunner._run_fallback(task, context, agents)
            
            env = {
                **os.environ,
                "PYTHONPATH": "/app",
                "METAGPT_PROJECT_ROOT": "/app",
                "HOME": "/root",
            }
            
            logger.info(f"Running MetaGPT team for task: {task[:80]}...")
            
            process = await asyncio.create_subprocess_exec(
                METAGPT_PYTHON, "-c", script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app",
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=json.dumps(input_data).encode()),
                timeout=timeout
            )
            
            stdout_str = stdout.decode().strip()
            stderr_str = stderr.decode()
            
            # Extract JSON using delimiters
            json_match = re.search(r'<<<JSON_START>>>(.*?)<<<JSON_END>>>', stdout_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    result = json.loads(json_str)
                    
                    # INJECT RAW LOGS INTO RESULT FOR VERBOSE DEBUGGING
                    result["raw_log"] = stderr_str
                    
                    logger.info(f"MetaGPT team completed with status: {result.get('status')}")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"JSON extract failed: {e}")
                    return {
                        "task": task,
                        "agent_outputs": {"raw_output": json_str[:2000]},
                        "final_synthesis": "Failed to parse JSON content",
                        "status": "PARSE_ERROR",
                        "error": str(e),
                        "raw_log": stderr_str
                    }
            
            # Fallback
            try:
                result = json.loads(stdout_str)
                result["raw_log"] = stderr_str
                return result
            except:
                logger.error(f"Could not find JSON delimiters")
                return {
                    "task": task,
                    "agent_outputs": {"raw_output": stdout_str[:2000]},
                    "final_synthesis": "No JSON output found",
                    "status": "PARSE_ERROR",
                    "error": "Missing JSON delimiters",
                    "raw_log": stderr_str + "\n\nSTDOUT:\n" + stdout_str
                }

        except asyncio.TimeoutError:
            logger.error(f"MetaGPT team execution timeout after {timeout}s")
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": "Team analysis timed out.",
                "status": "TIMEOUT",
                "error": "Execution timeout"
            }
        except Exception as e:
            logger.error(f"MetaGPT runner error: {e}")
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": f"Runner error: {str(e)}",
                "status": "ERROR",
                "error": str(e)
            }
    
    @staticmethod
    async def _run_fallback(
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fallback when MetaGPT venv not available - uses direct LLM"""
        try:
            from openai import AsyncOpenAI
            from config import settings
            
            logger.warning("Using LLM fallback (MetaGPT venv unavailable)")
            
            client = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )
            
            response = await client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a team of freelancer protection specialists. Analyze situations for risks, scams, and provide actionable advice. If you detect a scam, clearly state 'SCAM DETECTED'."},
                    {"role": "user", "content": task}
                ],
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            is_scam = any(w in content.lower() for w in ["scam", "fraud", "money laundering"])
            
            return {
                "task": task,
                "agent_outputs": {"llm_analysis": content},
                "final_synthesis": content,
                "status": "COMPLETED_FALLBACK",
                "risk_level": "HIGH" if is_scam else "LOW",
                "error": None
            }
        except Exception as e:
            return {
                "task": task,
                "agent_outputs": {},
                "final_synthesis": f"Fallback failed: {str(e)}",
                "status": "ERROR",
                "error": str(e)
            }
