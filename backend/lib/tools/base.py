"""
FlagPilot Tool Base Classes
===========================
Foundation for all agent tools with logging, metrics, and error handling.
"""

from typing import Any, Callable, Optional, Type
from functools import wraps
from loguru import logger
from pydantic import BaseModel
import time
import asyncio


class ToolMetrics:
    """Track tool usage metrics."""
    
    _calls: dict = {}
    _errors: dict = {}
    _latencies: dict = {}
    
    @classmethod
    def record_call(cls, tool_name: str, latency: float, success: bool):
        """Record a tool call."""
        if tool_name not in cls._calls:
            cls._calls[tool_name] = 0
            cls._errors[tool_name] = 0
            cls._latencies[tool_name] = []
        
        cls._calls[tool_name] += 1
        cls._latencies[tool_name].append(latency)
        
        if not success:
            cls._errors[tool_name] += 1
    
    @classmethod
    def get_stats(cls, tool_name: str = None) -> dict:
        """Get tool usage statistics."""
        if tool_name:
            latencies = cls._latencies.get(tool_name, [])
            return {
                "tool": tool_name,
                "calls": cls._calls.get(tool_name, 0),
                "errors": cls._errors.get(tool_name, 0),
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            }
        return {
            "total_calls": sum(cls._calls.values()),
            "total_errors": sum(cls._errors.values()),
            "tools": list(cls._calls.keys()),
        }


def track_tool(func: Callable) -> Callable:
    """Decorator to track tool execution metrics."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        success = True
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            logger.error(f"Tool {func.__name__} failed: {e}")
            raise
        finally:
            latency = time.perf_counter() - start
            ToolMetrics.record_call(func.__name__, latency, success)
            logger.debug(f"Tool {func.__name__} completed in {latency:.3f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        success = True
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            logger.error(f"Tool {func.__name__} failed: {e}")
            raise
        finally:
            latency = time.perf_counter() - start
            ToolMetrics.record_call(func.__name__, latency, success)
            logger.debug(f"Tool {func.__name__} completed in {latency:.3f}s")
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class ToolResult(BaseModel):
    """Standardized tool result format."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    source: str = "flagpilot"
    
    def to_string(self) -> str:
        """Format for LLM consumption."""
        if self.success:
            if isinstance(self.data, dict):
                return "\n".join(f"- {k}: {v}" for k, v in self.data.items())
            return str(self.data)
        return f"Error: {self.error}"


class ToolError(Exception):
    """Custom exception for tool failures."""
    def __init__(self, message: str, tool_name: str = None, recoverable: bool = True):
        self.message = message
        self.tool_name = tool_name
        self.recoverable = recoverable
        super().__init__(self.message)
