"""
RAGFlow Isolated Runner
========================
Executes RAGFlow SDK code in isolated venv via subprocess.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, List
from loguru import logger

RAGFLOW_VENV = os.environ.get("RAGFLOW_VENV", "/app/venv-ragflow")
RAGFLOW_PYTHON = os.path.join(RAGFLOW_VENV, "bin", "python")

if sys.platform == "win32":
    RAGFLOW_PYTHON = os.path.join(RAGFLOW_VENV, "Scripts", "python.exe")


class RAGFlowRunner:
    """Runs RAGFlow SDK code in isolated environment"""
    
    @staticmethod
    async def search(
        query: str,
        dataset_ids: Optional[List[str]] = None,
        limit: int = 5,
        timeout: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Search RAGFlow in the isolated environment.
        """
        input_data = {
            "query": query,
            "dataset_ids": dataset_ids,
            "limit": limit
        }
        
        script = '''
import sys
import json
import os

sys.path.insert(0, "/app")
os.chdir("/app")

input_data = json.loads(sys.stdin.read())

from ragflow import RAGFlow
from config import settings

client = RAGFlow(
    api_key=settings.RAGFLOW_API_KEY,
    base_url=settings.RAGFLOW_URL
)

results = client.search(
    query=input_data["query"],
    dataset_ids=input_data.get("dataset_ids"),
    limit=input_data.get("limit", 5)
)

output = [
    {"content": r.content, "similarity": r.similarity, "source": r.source}
    for r in results
]

print(json.dumps(output))
'''
        
        try:
            if not os.path.exists(RAGFLOW_PYTHON):
                logger.warning(f"RAGFlow venv not found at {RAGFLOW_PYTHON}, using fallback")
                return await RAGFlowRunner._run_fallback(query, dataset_ids, limit)
            
            process = await asyncio.create_subprocess_exec(
                RAGFLOW_PYTHON, "-c", script,
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
                logger.error(f"RAGFlow subprocess error: {error_msg}")
                return []
            
            return json.loads(stdout.decode())
            
        except asyncio.TimeoutError:
            logger.error("RAGFlow search timeout")
            return []
        except Exception as e:
            logger.error(f"RAGFlow runner error: {e}")
            return []
    
    @staticmethod
    async def _run_fallback(
        query: str,
        dataset_ids: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Fallback when venv not available"""
        try:
            from ragflow.client import get_ragflow_client
            client = get_ragflow_client()
            results = await client.search_user_context(
                user_id="default",
                query=query,
                limit=limit,
                dataset_ids=dataset_ids
            )
            return results
        except Exception as e:
            logger.error(f"RAGFlow fallback error: {e}")
            return []
