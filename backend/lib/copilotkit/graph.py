"""
FlagPilot LangGraph Workflow for CopilotKit
============================================
Wraps the multi-agent orchestrator in a CopilotKit-compatible workflow.

Uses CopilotKitState for proper AG-UI integration.
Messages must be added to the state for CopilotKit to display them.
"""

from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger

from lib.persistence import get_checkpointer

# CopilotKit State import for AG-UI compatibility
try:
    from copilotkit import CopilotKitState
    from copilotkit.langgraph import (
        copilotkit_emit_state,
        copilotkit_emit_message,
        copilotkit_exit,
    )
    COPILOTKIT_AVAILABLE = True
except ImportError:
    COPILOTKIT_AVAILABLE = False
    # Fallback for environments without copilotkit
    class CopilotKitState(TypedDict):
        messages: List
    
    async def copilotkit_emit_state(config, state):
        pass
    async def copilotkit_emit_message(config, message):
        pass
    async def copilotkit_exit(config):
        pass


class FlagPilotState(CopilotKitState):
    """State schema for FlagPilot CopilotKit workflow
    
    Inherits from CopilotKitState which provides the 'messages' field
    that CopilotKit uses for the chat UI.
    """
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
        # Handle different message formats (LangChain Message objects)
        if hasattr(msg, "content"):
            content = msg.content
            role = getattr(msg, "type", "")  # LangChain messages have 'type'
        elif isinstance(msg, dict):
            content = msg.get("content", "")
            role = msg.get("role", msg.get("type", ""))
        else:
            content = str(msg)
            role = ""
            
        # Check if it's a user message
        if role in ["user", "human"]:
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


async def credit_check_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Credit check node - validates user has enough credits before running agents.
    Returns error if insufficient credits.
    """
    from lib.billing.credits import credits_service
    
    # Get user_id from config
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id", "anonymous")
    
    if user_id == "anonymous":
        logger.info("Anonymous user - skipping credit check")
        return {"status": "credit_check_passed"}
    
    # Estimate agents that will be used
    estimated_agents = ["orchestrator", "contract-guardian", "job-authenticator", "risk-advisor"]
    
    try:
        check_result = await credits_service.check_credits(user_id, estimated_agents)
        
        if not check_result["allowed"]:
            logger.warning(f"Credit check failed for {user_id}: {check_result['reason']}")
            return {
                "messages": [AIMessage(content=f"⚠️ {check_result['reason']}\n\nYour current balance: {check_result['balance']} credits.")],
                "status": "CREDIT_ERROR",
                "error": check_result["reason"],
                "final_synthesis": check_result["reason"],
            }
        
        logger.info(f"Credit check passed: cost={check_result['cost']}, balance={check_result['balance']}")
        
        # Store info for deduction
        context = state.get("context", {}) or {}
        context["_credit_cost"] = check_result["cost"]
        context["_user_id"] = user_id
        context["_agents_used"] = estimated_agents
        
        return {"status": "credit_check_passed", "context": context}
        
    except Exception as e:
        logger.error(f"Credit check error: {e}")
        return {"status": "credit_check_passed"}


def should_continue_after_credit_check(state: FlagPilotState) -> str:
    """Route based on credit check result."""
    if state.get("status") == "CREDIT_ERROR":
        return "finalize"  # Skip to finalize with error
    return "orchestrate"


async def orchestrate_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Main orchestration node - runs the FlagPilot multi-agent team.
    Returns messages to be added to the chat.
    """
    from agents.orchestrator import run_orchestrator
    
    task = state.get("task", "")
    context = state.get("context", {}) or {}
    
    if not task:
        logger.warning("No task provided to orchestrate")
        # Return an AI message for the error
        return {
            "messages": [AIMessage(content="I didn't receive a message. How can I help you?")],
            "status": "error",
            "error": "No task provided",
            "final_synthesis": "I didn't receive a message. How can I help you?"
        }
    
    logger.info(f"Starting FlagPilot orchestration for: {task[:100]}...")
    
    try:
        # Emit initial planning state
        await copilotkit_emit_state(config, {
            "status": "planning",
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
        
        # Emit final state
        await copilotkit_emit_state(config, {
            "status": "complete",
            "current_agent": None,
            "risk_level": risk_level
        })
        
        logger.info(f"Orchestration complete. Status: {status}")
        
        # IMPORTANT: Return the AI message in the messages array
        # This is how CopilotKit receives the response
        return {
            "messages": [AIMessage(content=final_synthesis)] if final_synthesis else [],
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
        
        # Return error as AI message
        return {
            "messages": [AIMessage(content=error_message)],
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


async def credit_deduct_node(state: FlagPilotState, config) -> Dict[str, Any]:
    """
    Deduct credits after successful orchestration.
    Only deducts if orchestration was successful.
    """
    from lib.billing.credits import credits_service
    
    context = state.get("context", {}) or {}
    user_id = context.get("_user_id")
    agents_used = context.get("_agents_used", [])
    status = state.get("status", "")
    
    # Skip deduction if no user or if there was an error
    if not user_id or status in ["ERROR", "CREDIT_ERROR"]:
        logger.info("Skipping credit deduction (no user or error state)")
        return {}
    
    try:
        result = await credits_service.deduct_credits(user_id, agents_used)
        
        if result["success"]:
            logger.info(f"Credits deducted: user={user_id}, cost={result['cost']}, new_balance={result['new_balance']}")
        else:
            logger.warning(f"Credit deduction failed: {result.get('reason')}")
            
    except Exception as e:
        logger.error(f"Credit deduction error: {e}")
        # Don't fail the request for deduction errors
    
    return {}


# Build the LangGraph workflow
workflow = StateGraph(FlagPilotState)

# Add nodes
workflow.add_node("extract_task", extract_task_node)
workflow.add_node("credit_check", credit_check_node)
workflow.add_node("orchestrate", orchestrate_node)
workflow.add_node("credit_deduct", credit_deduct_node)
workflow.add_node("finalize", finalize_node)

# Set entry point
workflow.set_entry_point("extract_task")

# Add edges with conditional routing
workflow.add_edge("extract_task", "credit_check")
workflow.add_conditional_edges(
    "credit_check",
    should_continue_after_credit_check,
    {
        "orchestrate": "orchestrate",
        "finalize": "finalize",  # Skip to finalize on credit error
    }
)
workflow.add_edge("orchestrate", "credit_deduct")
workflow.add_edge("credit_deduct", "finalize")
workflow.add_edge("finalize", END)

# Compile with persistent checkpointer (PostgreSQL or fallback to memory)
checkpointer = get_checkpointer()
graph = workflow.compile(checkpointer=checkpointer)
