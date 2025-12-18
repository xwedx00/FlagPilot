"""
Base Role for all FlagPilot agents using MetaGPT

Provides streaming-capable agents with:
- Real-time status updates via async generators
- AG-UI Protocol compatible event formatting
- Credit consumption tracking
- Integration with the Data Moat
"""

import os
import time
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.llm import LLM
from metagpt.config2 import Config
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
import asyncio
import json
import uuid
from loguru import logger


# Import centralized LLM configuration
from config import get_configured_llm

from lib.agui.core import (
    EventType, CustomEvent, TextMessageChunkEvent, TextMessageContentEvent,
    StepStartedEvent, StepFinishedEvent
)


# Agent-to-UI event types for streaming (AG-UI Protocol Compatible)
class AgentEvent:
    """
    Events that agents emit during execution.
    Updated to return official AG-UI Event objects.
    """
    
    @staticmethod
    def thinking(agent_id: str, thought: str) -> CustomEvent:
        """Emit a custom thinking event"""
        return CustomEvent(
            name="agent_thinking",
            value={
                "agentId": agent_id,
                "thought": thought,
            }
        )
    
    @staticmethod
    def status(agent_id: str, status: str, action: str = None) -> CustomEvent:
        """Emit agent status update"""
        return CustomEvent(
            name="agent_status",
            value={
                "agentId": agent_id,
                "status": status,
                "action": action,
            }
        )
    
    @staticmethod
    def usage(agent_id: str, usage: Dict[str, int]) -> CustomEvent:
        """Emit token usage update (Production Enhancement)"""
        return CustomEvent(
            name="usage_update",
            value={
                "agentId": agent_id,
                "usage": usage,
                "timestamp": int(time.time() * 1000)
            }
        )
    
    @staticmethod
    def output(agent_id: str, content: str, message_id: str = None) -> TextMessageChunkEvent:
        """Emit agent output chunk"""
        return TextMessageChunkEvent(
            message_id=message_id or str(uuid.uuid4()),
            delta=content
        )
    
    @staticmethod
    def text_chunk(message_id: str, delta: str) -> TextMessageContentEvent:
        """Emit a text chunk"""
        return TextMessageContentEvent(
            message_id=message_id,
            delta=delta
        )
    
    @staticmethod
    def step_started(step_name: str) -> StepStartedEvent:
        """Emit step started"""
        return StepStartedEvent(step_name=step_name)
    
    @staticmethod
    def step_finished(step_name: str) -> StepFinishedEvent:
        """Emit step finished"""
        return StepFinishedEvent(step_name=step_name)
    
    @staticmethod
    def ui_component(component_name: str, props: Dict[str, Any]) -> CustomEvent:
        """Emit UI component"""
        return CustomEvent(
            name="ui_component",
            value={
                "componentName": component_name,
                "props": props,
            }
        )
    
    @staticmethod
    def artifact(name: str, artifact_type: str, content: str, agent_id: str) -> CustomEvent:
        """Emit artifact"""
        return CustomEvent(
            name="artifact",
            value={
                "name": name,
                "type": artifact_type,
                "content": content,
                "createdBy": agent_id,
            }
        )


class FlagPilotAction(Action):
    """Base action for FlagPilot agents with streaming support"""
    
    name: str = "FlagPilotAction"
    
    async def run(self, instruction: str, context: str = "", runtime_context: Dict[str, Any] = None) -> str:
        """Execute the action with LLM"""
        prompt = f"""
{self.desc}

Context:
{context}

Task:
{instruction}

Provide a detailed, actionable response.

!!! SAFETY PROTOCOL !!!
If you encounter a 'CRITICAL' risk (e.g., clear scam, illegal clause, malicious intent), you must set "is_critical_risk": true in your JSON response (if returning JSON) or clearly state "CRITICAL RISK DETECTED" at the start of your text output.
This will trigger a safety abort for the entire mission.
"""
        # Use our configured LLM instead of relying on MetaGPT context
        llm = get_configured_llm()
        response = await llm.aask(prompt)
        return response
    
    async def run_streaming(
        self, 
        instruction: str, 
        context: str = "",
        runtime_context: Dict[str, Any] = None,
        agent_id: str = "agent",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute action with streaming events"""
        # Emit thinking status
        yield AgentEvent.thinking(agent_id, f"Processing: {instruction[:50]}...")
        
        # Build prompt
        prompt = f"""
{self.desc}

Context:
{context}

Task:
{instruction}

Provide a detailed, actionable response.

!!! SAFETY PROTOCOL !!!
If you encounter a 'CRITICAL' risk (e.g., clear scam, illegal clause, malicious intent), you must set "is_critical_risk": true in your JSON response (if returning JSON) or clearly state "CRITICAL RISK DETECTED" at the start of your text output.
This will trigger a safety abort for the entire mission.
"""
        # Execute with LLM
        yield AgentEvent.status(agent_id, "working", "Generating response...")
        
        # Use our configured LLM instead of relying on MetaGPT context
        llm = get_configured_llm()
        response = await llm.aask(prompt)
        
        # Track usage (Simulated as we don't always get it from aask back directly in same object)
        # In production, we'd extract it from the LLM response object
        yield AgentEvent.usage(agent_id, {"prompt_tokens": len(prompt) // 4, "completion_tokens": len(response) // 4})
        
        # Emit output
        yield AgentEvent.output(agent_id, response)
        yield AgentEvent.status(agent_id, "done")


class AnalyzeAction(FlagPilotAction):
    """Generic analysis action"""
    name: str = "Analyze"
    desc: str = "Analyze the provided information and give expert insights."


class ReportAction(FlagPilotAction):
    """Generate report action"""
    name: str = "Report"
    desc: str = "Generate a comprehensive report based on analysis."


class FlagPilotRole(Role):
    """Base role for all FlagPilot agents"""
    
    name: str = "FlagPilotAgent"
    profile: str = "FlagPilot Specialist"
    goal: str = "Help freelancers succeed"
    constraints: str = "Be helpful, accurate, and actionable"
    
    
    def __init__(self, runtime_context: Dict[str, Any] = None, **kwargs):
        # Extract actions to prevent parent Role from crashing on non-instantiated classes
        raw_actions = kwargs.pop("actions", [])
        
        super().__init__(**kwargs)
        
        # self.rc is already initialized by Role.__init__ (MetaGPT standard)
        
        # Handle legacy runtime_context by keeping it for backward compatibility
        # We will merge it into context during _act
        self.runtime_context = runtime_context or {}
        
        # Initialize actions with auto-instantiation logic
        instantiated_actions = []
        for a in raw_actions:
            # Check if 'a' is a class (type) and subclass of Action/FlagPilotAction
            if isinstance(a, type):
                instantiated_actions.append(a())
            else:
                instantiated_actions.append(a)
        
        self.set_actions(instantiated_actions)
        self._watch(kwargs.get("watch", []))

    
    async def _act(self) -> Message:
        """Execute the role's action"""
        if not self.rc.todo:
            return None
            
        todo = self.rc.todo
        
        # Get context from memory
        context = self.get_memories()
        context_str = "\n".join([m.content for m in context]) if context else ""
        
        # Run the action
        # If the action has a run_streaming method, we should ideally use that for detailed events,
        # but for standard _act from Team.run(), we fallback to standard run()
        
        # Extract instruction from the causing message if available
        instruction = ""
        if self.rc.important_memory:
            instruction = self.rc.important_memory[-1].content
            
        # Merge runtime_context with standard MetaGPT context (self.context)
        # This allows hybrid usage: standard Team execution OR manual orchestration
        final_context = {}
        
        # 1. Standard MetaGPT Context (from Team/Env via RoleContext)
        # self.rc.env might be None if just instantiated
        if self.rc.env and self.rc.env.context:
             final_context.update(self.rc.env.context.kwargs)
        elif hasattr(self, "context") and self.context:
            # Fallback to standard MetaGPT role.context injection
            final_context.update(self.context.kwargs)
            
        # 2. Runtime Context (Manual Overrides - Deprecated but supported)
        if self.runtime_context:
            final_context.update(self.runtime_context)
            
        result = await todo.run(
            instruction=instruction,
            context=context_str,
            runtime_context=final_context
        )
        
        msg = Message(
            content=result,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
        )
        
        return msg
    
    async def analyze(self, input_text: str, context: dict = None) -> str:
        """Direct analysis method for API calls"""
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        action = AnalyzeAction()
        action.desc = f"You are {self.name}, {self.profile}. {self.goal}"
        
        # Ensure action has access to RoleContext if needed (uncommon for ad-hoc analyze)
        
        result = await action.run(
            instruction=input_text,
            context=context_str,
            runtime_context=context
        )
        
        return result
    
    async def analyze_streaming(
        self, 
        input_text: str, 
        context: dict = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming analysis method for SSE endpoints"""
        agent_id = self.name.lower().replace(" ", "-")
        
        # Emit starting status
        yield AgentEvent.status(agent_id, "thinking", "Analyzing input...")
        
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        action = AnalyzeAction()
        action.desc = f"You are {self.name}, {self.profile}. {self.goal}"
        
        yield AgentEvent.thinking(agent_id, f"Processing request...")
        
        # Run the analysis
        async for event in action.run_streaming(
            instruction=input_text,
            context=context_str,
            runtime_context=context,
            agent_id=agent_id,
        ):
            yield event
    
    def get_agent_id(self) -> str:
        """Get standardized agent ID for events"""
        return self.name.lower().replace(" ", "-")
    
    def get_credit_cost(self) -> int:
        """Get the credit cost for this agent's tasks"""
        # Default costs by agent type
        COSTS = {
            "contract-guardian": 25,
            "legal-eagle": 25,
            "job-authenticator": 5,
            "payment-enforcer": 10,
            "negotiator": 20,
            "iris": 15,
            "adjudicator": 15,
            "scope-sentinel": 10,
            "coach": 5,
            "sentinel": 5,
            "ledger": 5,
            "scribe": 3,
            "connector": 2,
            "vault-keeper": 2,
            "flagpilot": 0,  # Orchestrator is free
        }
        return COSTS.get(self.get_agent_id(), 5)
