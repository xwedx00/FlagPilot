"""
DAG Executor - Parallel Task Execution Engine

Executes workflow DAGs with:
- Dependency-aware scheduling
- Parallel execution (Race Mode)
- Streaming progress updates
- Error handling and recovery
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
from loguru import logger

from .schemas import WorkflowPlan, TaskNode, TaskStatus


class DAGExecutor:
    """
    Execute workflow DAGs with parallel task execution.
    
    Features:
    - Dependency-aware scheduling (respects task dependencies)
    - Parallel execution (tasks without dependencies run together)
    - Streaming progress (yields events for real-time UI updates)
    - Error handling (continues workflow when individual tasks fail)
    """
    
    def __init__(
        self,
        agent_executor: Optional[Callable[[TaskNode, str, Dict], Awaitable[Dict]]] = None,
        max_parallel: int = 4,
    ):
        """
        Initialize the DAG executor.
        
        Args:
            agent_executor: Async function to execute a task. 
                           Signature: (task, user_id, context) -> {"output": str, "ui_component": optional}
            max_parallel: Maximum number of tasks to run in parallel
        """
        self.agent_executor = agent_executor or self._default_executor
        self.max_parallel = max_parallel
    
    async def execute(
        self,
        plan: WorkflowPlan,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a workflow plan, yielding progress events.
        
        Events yielded:
        - workflow_start: Execution beginning
        - workflow_update: DAG state changed (for visualization)
        - agent_start: Agent beginning work
        - agent_thinking: Agent thought process
        - agent_output: Partial agent output
        - agent_finish: Agent completed
        - agent_error: Agent failed
        - ui_component: Generative UI to render
        - workflow_complete: All done
        
        Args:
            plan: The workflow plan to execute
            user_id: User ID for context
            context: Additional execution context
        
        Yields:
            Event dictionaries for the frontend
        """
        logger.info(f"Starting workflow execution: {plan.id}")
        
        # Initial event
        yield {
            "type": "workflow_start",
            "workflow_id": plan.id,
            "objective": plan.objective,
            "total_tasks": len(plan.nodes),
        }
        
        # Send initial DAG state
        yield {
            "type": "workflow_update",
            **plan.to_react_flow(),
        }
        
        # Execute until all tasks complete
        iteration = 0
        max_iterations = len(plan.nodes) * 2  # Safety limit
        
        while not plan.is_complete() and iteration < max_iterations:
            iteration += 1
            
            ready_tasks = plan.get_ready_tasks()
            
            if not ready_tasks:
                # Check for deadlock
                pending = plan.get_pending_tasks()
                running = plan.get_running_tasks()
                
                if pending and not running:
                    # Deadlock - mark remaining as failed
                    logger.error(f"Workflow deadlock detected: {[n.id for n in pending]}")
                    for task in pending:
                        task.fail("Deadlock: dependencies cannot be satisfied")
                    break
                elif running:
                    # Wait for running tasks
                    await asyncio.sleep(0.1)
                    continue
                else:
                    break
            
            # Execute ready tasks in parallel (up to max_parallel)
            batch = ready_tasks[:self.max_parallel]
            
            # Mark as running and emit start events
            for task in batch:
                task.start()
                yield {
                    "type": "agent_start",
                    "task_id": task.id,
                    "agent": task.agent,
                    "instruction": task.instruction,
                }
            
            # Update visualization
            yield {
                "type": "workflow_update",
                **plan.to_react_flow(),
            }
            
            # Execute batch in parallel
            results = await asyncio.gather(
                *[
                    self._execute_task_safe(task, user_id, context or {})
                    for task in batch
                ],
                return_exceptions=True,
            )
            
            # Process results
            for task, result in zip(batch, results):
                if isinstance(result, Exception):
                    task.fail(str(result))
                    yield {
                        "type": "agent_error",
                        "task_id": task.id,
                        "agent": task.agent,
                        "error": str(result),
                    }
                else:
                    output = result.get("output", "")
                    task.complete(output)
                    
                    yield {
                        "type": "agent_finish",
                        "task_id": task.id,
                        "agent": task.agent,
                        "output": output[:1000] if output else "",
                    }
                    
                    # Forward any UI components
                    if "ui_component" in result:
                        yield {
                            "type": "ui_component",
                            **result["ui_component"],
                        }
                    
                    # Forward any messages
                    if "message" in result:
                        yield {
                            "type": "message",
                            "agent": task.agent,
                            "content": result["message"],
                        }
            
            # Update visualization
            yield {
                "type": "workflow_update",
                **plan.to_react_flow(),
            }
        
        # Final completion event
        plan.status = TaskStatus.COMPLETED if plan.is_complete() else TaskStatus.FAILED
        
        yield {
            "type": "workflow_complete",
            "workflow_id": plan.id,
            "status": plan.status.value,
            "completion": plan.get_completion_percentage(),
            "results": {
                node.id: node.result
                for node in plan.nodes
                if node.result
            },
        }
        
        logger.info(f"Workflow {plan.id} complete: {plan.status.value}")
    
    async def _execute_task_safe(
        self,
        task: TaskNode,
        user_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a task with error handling"""
        try:
            return await self.agent_executor(task, user_id, context)
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            raise
    
    async def _default_executor(
        self,
        task: TaskNode,
        user_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Default task executor that uses the agent registry.
        
        This can be overridden by providing a custom agent_executor
        to the DAGExecutor constructor.
        """
        try:
            # Import here to avoid circular imports
            from agents import AGENT_REGISTRY
            
            agent_cls = AGENT_REGISTRY.get(task.agent)
            if not agent_cls:
                return {"output": f"Agent {task.agent} not found"}
            
            agent = agent_cls()
            # Execute agent analysis
            result = await agent.analyze(task.instruction, context)
            
            return {
                "output": result if isinstance(result, str) else str(result),
            }
            
        except ImportError:
            # Fallback if agents module not available
            logger.warning(f"Agents module not available, using simulation for {task.agent}")
            await asyncio.sleep(1)  # Simulate work
            return {
                "output": f"[Simulated] {task.agent} completed: {task.instruction[:100]}",
            }


async def execute_workflow(
    plan: WorkflowPlan,
    user_id: str,
    context: Optional[Dict[str, Any]] = None,
    max_parallel: int = 4,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Convenience function to execute a workflow.
    
    Args:
        plan: The workflow plan
        user_id: User ID
        context: Additional context
        max_parallel: Max parallel tasks
    
    Yields:
        Execution events
    """
    executor = DAGExecutor(max_parallel=max_parallel)
    async for event in executor.execute(plan, user_id, context):
        yield event
