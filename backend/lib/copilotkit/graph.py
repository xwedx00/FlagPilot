"""
FlagPilot LangGraph Workflow
============================
Wraps MetaGPT agents in a LangGraph workflow for CopilotKit integration.

The workflow:
1. Receives user task from CopilotKit
2. Runs FlagPilotTeam orchestration (MetaGPT)
3. Emits progress updates via CopilotKit SDK
4. Returns final synthesis
"""

from typing import TypedDict, Optional, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from loguru import logger

# CopilotKit LangGraph SDK imports
try:
    from copilotkit.langgraph import (
        copilotkit_emit_state,
        copilotkit_emit_message,
        copilotkit_exit,
        copilotkit_customize_config
    )
except ImportError:
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
    """State schema for FlagPilot LangGraph workflow"""
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
    orchestrator_analysis: Optional[Dict[str, Any]]
    final_synthesis: Optional[str]
    risk_level: str
    
    # Error handling
    error: Optional[str]


async def extract_task_node(state: FlagPilotState, config) -> FlagPilotState:
    """
    Extract the task from incoming messages.
    This is the entry point for CopilotKit messages.
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
        if role in ["user", "human"]:
            task = content
            break
    
    if not task:
        # Fallback to state task if no message found
        task = state.get("task", "")
    
    logger.info(f"Task extracted: {task[:100]}...")
    
    return {
        **state,
        "task": task,
        "status": "task_extracted"
    }


async def orchestrate_node(state: FlagPilotState, config) -> FlagPilotState:
    """
    Main orchestration node - runs the FlagPilotTeam.
    Uses isolated MetaGPT runner to avoid dependency conflicts.
    """
    from lib.runners.metagpt_runner import MetaGPTRunner
    
    task = state.get("task", "")
    context = state.get("context", {})
    
    if not task:
        logger.warning("No task provided to orchestrate")
        return {
            **state,
            "status": "error",
            "error": "No task provided",
            "final_synthesis": "I didn't receive a message. How can I help you?"
        }
    
    logger.info(f"Starting FlagPilot Team orchestration for: {task[:100]}...")
    
    try:
        # Emit initial state
        await copilotkit_emit_state(config, {
            "status": "planning",
            "agents": [],
            "current_agent": None,
            "risk_level": "none"
        })
        
        # Emit planning status
        await copilotkit_emit_state(config, {
            "status": "executing",
            "current_agent": "orchestrator"
        })
        
        # Run the orchestration in isolated MetaGPT environment
        result = await MetaGPTRunner.run_team(task=task, context=context)
        
        # Extract results
        agent_outputs = result.get("agent_outputs", {})
        final_synthesis = result.get("final_synthesis", "")
        status = result.get("status", "COMPLETED")
        risk_level = result.get("risk_level", "none")
        error = result.get("error")
        
        if error:
            logger.warning(f"MetaGPT execution had error: {error}")
        
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
            **state,
            "status": status,
            "agent_outputs": agent_outputs,
            "final_synthesis": final_synthesis,
            "risk_level": risk_level,
            "current_agent": None,
            "error": error
        }
        
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        error_message = f"An error occurred during analysis: {str(e)}"
        
        await copilotkit_emit_state(config, {
            "status": "error",
            "error": str(e)
        })
        
        return {
            **state,
            "status": "ERROR",
            "error": str(e),
            "final_synthesis": error_message
        }


async def finalize_node(state: FlagPilotState, config) -> FlagPilotState:
    """
    Finalize the workflow and signal completion to CopilotKit.
    """
    logger.info("Finalizing workflow...")
    
    # Signal CopilotKit that the agent is done
    await copilotkit_exit(config)
    
    return state


def should_continue(state: FlagPilotState) -> str:
    """Determine if we should continue or end the workflow."""
    status = state.get("status", "")
    error = state.get("error")
    
    if error or status in ["ERROR", "BLOCKED", "ABORTED_ON_RISK"]:
        return "finalize"
    
    if status in ["COMPLETED", "COMPLETED_DIRECT", "WAITING_FOR_USER"]:
        return "finalize"
    
    return "orchestrate"


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

# Compile the graph
graph = workflow.compile()
