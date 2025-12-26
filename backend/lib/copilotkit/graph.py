"""
FlagPilot LangGraph Workflow for CopilotKit
============================================
Wraps the multi-agent orchestrator in a CopilotKit-compatible workflow.

Features:
- Message extraction from CopilotKit
- State emission via copilotkit_emit_state
- Message streaming via copilotkit_emit_message
- Proper exit signaling
"""

from typing import TypedDict, Optional, Dict, Any, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger

# CopilotKit LangGraph SDK imports
try:
    from copilotkit.langgraph import (
        copilotkit_emit_state,
        copilotkit_emit_message,
        copilotkit_exit,
        copilotkit_customize_config
    )
    COPILOTKIT_AVAILABLE = True
except ImportError:
    COPILOTKIT_AVAILABLE = False
    # Fallback for environments without copilotkit
    async def copilotkit_emit_state(config, state):
        pass
    async def copilotkit_emit_message(config, message):
        pass
    async def copilotkit_exit(config):
        pass
    def copilotkit_customize_config(config, **kwargs):
        return config


class FlagPilotState(TypedDict):
    """State schema for FlagPilot CopilotKit workflow"""
    # CopilotKit message history
    messages: Annotated[list, add_messages]
    
    # Task information
    task: str
    context: Optional[Dict[str, Any]]
    
    # Execution state
    status: str
    current_agent: Optional[str]
    agent_outputs: Dict[str, str]
    
    # Results
    final_synthesis: Optional[str]
    risk_level: str
    is_critical_risk: bool
    
    # Error handling
    error: Optional[str]


async def extract_task_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Extract the task from incoming CopilotKit messages.
    This is the entry point for the workflow.
    """
    logger.info("Extracting task from messages...")
    
    # Get the last user message as the task
    task = ""
    for msg in reversed(state.get("messages", [])):
        # Handle different message formats
        if hasattr(msg, "content"):
            content = msg.content
        elif isinstance(msg, dict):
            content = msg.get("content", "")
        else:
            content = str(msg)
            
        # Check if it's a user message
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else None)
        msg_type = getattr(msg, "type", None) or (msg.get("type") if isinstance(msg, dict) else None)
        
        if role in ["user", "human"] or msg_type == "human":
            task = content
            break
    
    if not task:
        # Fallback to state task if no message found
        task = state.get("task", "")
    
    logger.info(f"Task extracted: {task[:100]}...")
    
    return {
        "task": task,
        "status": "task_extracted"
    }


async def orchestrate_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Main orchestration node - runs the FlagPilot multi-agent team.
    Uses the new LangGraph orchestrator directly.
    """
    from agents.orchestrator import run_orchestrator
    
    task = state.get("task", "")
    context = state.get("context", {}) or {}
    
    if not task:
        logger.warning("No task provided to orchestrate")
        return {
            "status": "error",
            "error": "No task provided",
            "final_synthesis": "I didn't receive a message. How can I help you?"
        }
    
    logger.info(f"Starting FlagPilot orchestration for: {task[:100]}...")
    
    try:
        # Emit initial planning state
        await copilotkit_emit_state(config, {
            "status": "planning",
            "agents": [],
            "current_agent": "orchestrator",
            "risk_level": "none"
        })
        
        # Run the orchestrator
        result = await run_orchestrator(task=task, context=context)
        
        # Extract results
        agent_outputs = result.get("agent_outputs", {})
        final_synthesis = result.get("final_synthesis", "")
        status = result.get("status", "COMPLETED")
        risk_level = result.get("risk_level", "LOW")
        is_critical = result.get("is_critical_risk", False)
        
        # Emit progress for each agent that ran
        for agent_id in agent_outputs.keys():
            await copilotkit_emit_state(config, {
                "status": "agent_complete",
                "current_agent": agent_id
            })
        
        # Emit final state
        await copilotkit_emit_state(config, {
            "status": "complete",
            "current_agent": None,
            "risk_level": risk_level
        })
        
        # Emit the final message
        if final_synthesis:
            await copilotkit_emit_message(config, final_synthesis)
        
        logger.info(f"Orchestration complete. Status: {status}")
        
        return {
            "status": status,
            "agent_outputs": agent_outputs,
            "final_synthesis": final_synthesis,
            "risk_level": risk_level,
            "is_critical_risk": is_critical,
            "current_agent": None,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        error_message = f"An error occurred during analysis: {str(e)}"
        
        await copilotkit_emit_state(config, {
            "status": "error",
            "error": str(e)
        })
        
        return {
            "status": "ERROR",
            "error": str(e),
            "final_synthesis": error_message
        }


async def finalize_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Finalize the workflow and signal completion to CopilotKit.
    """
    logger.info("Finalizing workflow...")
    
    # Signal CopilotKit that the agent is done
    await copilotkit_exit(config)
    
    return {}


# Build the LangGraph workflow
workflow = StateGraph(FlagPilotState)

# Add nodes
workflow.add_node("extract_task", extract_task_node)
workflow.add_node("orchestrate", orchestrate_node)
workflow.add_node("finalize", finalize_node)

# Set entry point
workflow.set_entry_point("extract_task")

# Add edges
workflow.add_edge("extract_task", "orchestrate")
workflow.add_edge("orchestrate", "finalize")
workflow.add_edge("finalize", END)

# Compile with memory saver for persistence
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
