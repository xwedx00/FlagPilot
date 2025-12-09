"""
Dynamic DAG (Directed Acyclic Graph) Module

Implements dynamic workflow generation and parallel execution:
- LLM-based DAG generation from user requests
- Parallel task execution (Race Mode)
- React Flow compatible serialization
"""

from .schemas import WorkflowPlan, TaskNode, TaskStatus
from .generator import generate_workflow_plan
from .executor import DAGExecutor

__all__ = [
    "WorkflowPlan", 
    "TaskNode", 
    "TaskStatus",
    "generate_workflow_plan",
    "DAGExecutor",
]
