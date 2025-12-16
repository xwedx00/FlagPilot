"""
Simplified Agent Router
=======================
Exposes MetaGPT agents as simple chat endpoints.
Frontend (Vercel AI SDK) handles orchestration via tool calling.

Endpoints:
- GET  /api/agents              - List all agents
- GET  /api/agents/{agent_id}   - Get agent details
- POST /api/agents/{agent_id}/chat - Chat with agent (SSE streaming)
- POST /api/team/chat           - Team orchestration (SSE streaming)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from agents.registry import registry
from agents.team import FlagPilotTeam
import json
import asyncio
from loguru import logger

router = APIRouter(prefix="/api", tags=["Agents"])


class ChatRequest(BaseModel):
    """Request body for agent chat"""
    message: str
    context: Optional[Dict[str, Any]] = None


class TeamChatRequest(BaseModel):
    """Request body for team orchestration"""
    message: str
    context: Optional[Dict[str, Any]] = None
    agents: Optional[List[str]] = None  # Specific agents to use, None = all


def format_sse(event: str, data: Any) -> str:
    """Format data as SSE event"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.get("/agents")
async def list_agents():
    """
    List all available agents.
    
    Returns agent IDs that can be used with /api/agents/{agent_id}/chat
    """
    agents_list = registry.list_agents()
    return {
        "agents": agents_list,
        "count": len(agents_list)
    }


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get details about a specific agent.
    
    Returns agent profile, goal, and capabilities.
    """
    agent_cls = registry.get_agent_class(agent_id)
    if not agent_cls:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Use GET /api/agents for available agents."
        )
    
    # Instantiate to get profile info
    agent = agent_cls()
    
    return {
        "id": agent_id,
        "name": agent.name,
        "profile": agent.profile,
        "goal": agent.goal,
        "constraints": agent.constraints,
    }


@router.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """
    Chat with a specific agent via SSE streaming.
    
    Events emitted:
    - agent_status: Agent state changes (thinking, working, done)
    - agent_thinking: Agent thought process
    - message: Agent response content
    - error: If something goes wrong
    - [DONE]: Stream complete
    """
    agent_cls = registry.get_agent_class(agent_id)
    if not agent_cls:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Use GET /api/agents for available agents."
        )
    
    agent = agent_cls()
    
    async def generate():
        try:
            # Yield connection confirmation
            yield format_sse("connected", {"agent_id": agent_id, "status": "connected"})
            
            # Stream agent analysis
            async for event in agent.analyze_streaming(request.message, request.context):
                event_type = event.get("type", "message")
                yield format_sse(event_type, event)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Agent {agent_id} error: {e}")
            yield format_sse("error", {"error": str(e)})
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/team/chat")
async def team_chat(request: TeamChatRequest):
    """
    Run team orchestration via SSE streaming.
    
    The FlagPilot orchestrator will:
    1. Analyze the task
    2. Identify relevant agents
    3. Coordinate their work
    4. Synthesize a final response
    
    Events emitted:
    - connected: Initial connection
    - agent_status: Per-agent status changes
    - agent_thinking: Agent thought processes
    - message: Agent outputs
    - synthesis: Final synthesized response
    - error: If something goes wrong
    - [DONE]: Stream complete
    """
    team = FlagPilotTeam(agents=request.agents)
    
    async def generate():
        try:
            yield format_sse("connected", {"status": "team_initialized"})
            
            # Run team orchestration
            result = await team.run(
                task=request.message,
                context=request.context,
                n_round=3
            )
            
            # Yield final result
            yield format_sse("synthesis", {
                "type": "synthesis",
                "content": result.get("synthesis", result.get("result", "")),
                "agents_used": result.get("agents_used", []),
            })
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Team orchestration error: {e}")
            yield format_sse("error", {"error": str(e)})
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
