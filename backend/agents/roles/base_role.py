"""
Base Role for all FlagPilot agents using MetaGPT

Provides streaming-capable agents with:
- Real-time status updates via async generators
- Vercel AI SDK compatible output formatting
- Credit consumption tracking
- Integration with the Data Moat
"""

import os
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


# Agent-to-UI event types for streaming
class AgentEvent:
    """Events that agents emit during execution"""
    
    @staticmethod
    def thinking(agent_id: str, thought: str) -> Dict[str, Any]:
        return {
            "type": "agent_thinking",
            "agentId": agent_id,
            "thought": thought,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def status(agent_id: str, status: str, action: str = None) -> Dict[str, Any]:
        return {
            "type": "agent_status",
            "agentId": agent_id,
            "status": status,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def output(agent_id: str, content: str) -> Dict[str, Any]:
        return {
            "type": "message",
            "agentId": agent_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def ui_component(component_name: str, props: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "ui_component",
            "componentName": component_name,
            "props": props,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def artifact(name: str, artifact_type: str, content: str, agent_id: str) -> Dict[str, Any]:
        return {
            "type": "artifact",
            "artifact": {
                "name": name,
                "type": artifact_type,
                "content": content,
                "createdBy": agent_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


class FlagPilotAction(Action):
    """Base action for FlagPilot agents with streaming support"""
    
    name: str = "FlagPilotAction"
    
    async def run(self, instruction: str, context: str = "") -> str:
        """Execute the action with LLM"""
        prompt = f"""
{self.desc}

Context:
{context}

Task:
{instruction}

Provide a detailed, actionable response.
"""
        # Use our configured LLM instead of relying on MetaGPT context
        llm = get_configured_llm()
        response = await llm.aask(prompt)
        return response
    
    async def run_streaming(
        self, 
        instruction: str, 
        context: str = "",
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
"""
        # Execute with LLM
        yield AgentEvent.status(agent_id, "working", "Generating response...")
        
        # Use our configured LLM instead of relying on MetaGPT context
        llm = get_configured_llm()
        response = await llm.aask(prompt)
        
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeAction])
        self._watch([])  # Can watch other roles' messages
    
    async def _act(self) -> Message:
        """Execute the role's action"""
        todo = self.rc.todo
        
        # Get context from memory
        context = self.get_memories()
        context_str = "\n".join([m.content for m in context]) if context else ""
        
        # Run the action
        result = await todo.run(
            instruction=self.rc.important_memory[-1].content if self.rc.important_memory else "",
            context=context_str
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
        
        result = await action.run(
            instruction=input_text,
            context=context_str
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
