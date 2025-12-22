"""
RAGFlow Isolated Runner
========================
Executes RAGFlow SDK code in isolated venv via subprocess.
Settings are passed via input data to avoid pydantic_settings dependency.
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
        # Get settings from core environment
        from config import settings
        
        input_data = {
            "query": query,
            "dataset_ids": dataset_ids,
            "limit": limit,
            # Pass settings directly to avoid config import in subprocess
            "ragflow_api_key": settings.RAGFLOW_API_KEY,
            "ragflow_url": settings.RAGFLOW_URL
        }
        
        # Script that doesn't import config.py
        script = '''
import sys
import json
import os

sys.path.insert(0, "/app")
os.chdir("/app")

input_data = json.loads(sys.stdin.read())

try:
    from ragflow_sdk import RAGFlow
    
    api_key = input_data.get("ragflow_api_key", "")
    base_url = input_data.get("ragflow_url", "http://ragflow:80")
    
    client = RAGFlow(
        api_key=api_key,
        base_url=base_url
    )
    
    # Try to list datasets first
    datasets = client.list_datasets()
    
    # Search across datasets
    results = []
    query = input_data["query"]
    limit = input_data.get("limit", 5)
    
    for ds in datasets[:3]:  # Search first 3 datasets
        try:
            chunks = ds.retrieve(
                question=query,
                datasets=[ds.id],
                top_k=limit
            )
            for chunk in chunks:
                results.append({
                    "content": getattr(chunk, "content", str(chunk)),
                    "similarity": getattr(chunk, "similarity", 0.0),
                    "source": getattr(chunk, "document_name", "unknown")
                })
        except Exception as e:
            pass  # Skip datasets that don't support retrieval
    
    print(json.dumps(results[:limit]))
    
except ImportError as e:
    # ragflow_sdk not installed
    print(json.dumps([]))
except Exception as e:
    print(json.dumps([{"error": str(e)}]))
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
            
            result = json.loads(stdout.decode())
            if result and isinstance(result, list) and len(result) > 0:
                if "error" in result[0]:
                    logger.warning(f"RAGFlow search warning: {result[0]['error']}")
                    return []
            return result
            
        except asyncio.TimeoutError:
            logger.error("RAGFlow search timeout")
            return []
        except Exception as e:
            logger.error(f"RAGFlow runner error: {e}")
            return []
    
    @staticmethod
    async def health_check(timeout: int = 30) -> Dict[str, Any]:
        """Check RAGFlow health via isolated venv"""
        from config import settings
        
        input_data = {
            "ragflow_api_key": settings.RAGFLOW_API_KEY,
            "ragflow_url": settings.RAGFLOW_URL
        }
        
        script = '''
import sys
import json
import os

sys.path.insert(0, "/app")
input_data = json.loads(sys.stdin.read())

try:
    from ragflow_sdk import RAGFlow
    
    client = RAGFlow(
        api_key=input_data.get("ragflow_api_key", ""),
        base_url=input_data.get("ragflow_url", "http://ragflow:80")
    )
    
    # Try listing datasets as health check
    datasets = client.list_datasets()
    
    print(json.dumps({
        "status": "healthy",
        "connected": True,
        "datasets_count": len(datasets)
    }))
    
except ImportError as e:
    print(json.dumps({
        "status": "sdk_not_installed",
        "connected": False,
        "error": str(e)
    }))
except Exception as e:
    print(json.dumps({
        "status": "error",
        "connected": False,
        "error": str(e)
    }))
'''
        
        try:
            if not os.path.exists(RAGFLOW_PYTHON):
                return {"status": "venv_not_found", "connected": False}
            
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
                return {"status": "error", "connected": False, "error": stderr.decode()}
            
            return json.loads(stdout.decode())
            
        except Exception as e:
            return {"status": "error", "connected": False, "error": str(e)}
    
    @staticmethod
    async def upload_document(
        dataset_name: str,
        content: str,
        blob_name: str = "test_doc.txt",
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Upload text content to RAGFlow dataset via isolated venv.
        """
        from config import settings
        
        input_data = {
            "dataset_name": dataset_name,
            "content": content,
            "blob_name": blob_name,
            "ragflow_api_key": settings.RAGFLOW_API_KEY,
            "ragflow_url": settings.RAGFLOW_URL
        }
        
        script = '''
import sys
import json
import os
import tempfile

sys.path.insert(0, "/app")
input_data = json.loads(sys.stdin.read())

try:
    from ragflow_sdk import RAGFlow
    
    client = RAGFlow(
        api_key=input_data.get("ragflow_api_key", ""),
        base_url=input_data.get("ragflow_url", "http://ragflow:80")
    )
    
    # Check or create dataset
    dataset_name = input_data.get("dataset_name", "custom_kb")
    dataset = None
    
    try:
        datasets = client.list_datasets(page=1, page_size=100)
        for ds in datasets:
            if ds.name == dataset_name:
                dataset = ds
                break
    except Exception as e:
        print(f"List datasets warning: {e}", file=sys.stderr)
        
    if not dataset:
        try:
            dataset = client.create_dataset(name=dataset_name)
            print(f"Created dataset: {dataset_name}", file=sys.stderr)
        except Exception as e:
            # Maybe it exists but listing failed or race condition
            print(f"Create dataset error: {e}", file=sys.stderr)
            # Try to find again strictly
            datasets = client.list_datasets()
            for ds in datasets:
                if ds.name == dataset_name:
                    dataset = ds
                    break
    
    if not dataset:
        print(json.dumps({"error": "Could not create or find dataset"}))
        sys.exit(0)
        
    # Write content to temp file
    blob_name = input_data.get("blob_name", "doc.txt")
    temp_path = os.path.join("/tmp", blob_name)
    
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(input_data.get("content", ""))
        
    # Upload document
    print(f"Uploading {blob_name} to {dataset_name}...", file=sys.stderr)
    
    # RAGFlow SDK upload requires a file object opened in binary mode usually, 
    # but let's try standard upload_documents method
    
    with open(temp_path, "rb") as f:
        # Note: SDK signature might vary, usually upload_documents(file_list=[...])
        # Using blob specifically
        blob = f.read()
        try:
            res = dataset.upload_documents([{"display_name": blob_name, "blob": blob}])
            # res might be a list of objects, not serializable
            print(json.dumps({"status": "success", "message": "Upload call completed"}), file=sys.stdout)
        except Exception as upload_err:
             print(json.dumps({"status": "error", "error": str(upload_err)}), file=sys.stdout)

except Exception as e:
    import traceback
    print(json.dumps({"error": str(e), "traceback": traceback.format_exc()}))
'''
        
        try:
            if not os.path.exists(RAGFLOW_PYTHON):
                return {"error": "RAGFlow venv not found"}
            
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
            
            result = {}
            if stdout:
                try:
                    result = json.loads(stdout.decode())
                except:
                    result = {"raw_stdout": stdout.decode()}
            
            result["raw_log"] = stderr.decode() if stderr else ""
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

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
