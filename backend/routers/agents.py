"""
AG-UI Protocol Router for FlagPilot
====================================
Implements the AG-UI (Agent-User Interaction) protocol using the official SDK.

Official SDK: pip install ag-ui-protocol
AG-UI Protocol Reference: https://docs.ag-ui.com/sdk/python/core

Endpoints:
- POST /api/agui                - AG-UI protocol endpoint (main)
- POST /api/team/chat           - Team orchestration (AG-UI stream)
- POST /api/agents/{id}/chat    - Single agent (AG-UI stream)
- GET  /api/agents              - List available agents
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from agents.registry import registry
from agents.team import FlagPilotTeam
import uuid
import asyncio
from loguru import logger


from lib.agui.core import (
    EventType, RunAgentInput, Message, Context, Tool,
    RunStartedEvent, RunFinishedEvent, RunErrorEvent,
    StepStartedEvent, StepFinishedEvent,
    TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent, TextMessageChunkEvent,
    StateSnapshotEvent, StateDeltaEvent, MessagesSnapshotEvent,
    ActivitySnapshotEvent, CustomEvent
)
from lib.agui.encoder import EventEncoder

router = APIRouter(prefix="/api", tags=["AG-UI Agents"])

# Global run registry for cancellation (simplified for production demo)
active_runs: Dict[str, asyncio.Task] = {}
run_states: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# Helper Functions
# =============================================================================

def get_last_user_message(messages: List[Message]) -> str:
    """Extract the last user message content"""
    for msg in reversed(messages):
        if msg.role == "user" and msg.content:
            return msg.content
    return ""


def build_context_dict(input_data: RunAgentInput) -> Dict[str, Any]:
    """Build context dictionary from AG-UI input"""
    ctx = {"threadId": input_data.thread_id, "runId": input_data.run_id}
    
    # Add context items
    for c in input_data.context:
        ctx[c.description] = c.value
    
    # Add state
    if input_data.state:
        if isinstance(input_data.state, dict):
            ctx.update(input_data.state)
    
    return ctx


# =============================================================================
# Production Management Endpoints
# =============================================================================

@router.get("/agents/{agent_id}/state")
async def get_agent_state(agent_id: str):
    """Fetch the current state of an agent"""
    # In a real system, this would fetch from a database or distributed cache
    # For now, we return the last known state from run_states or a default
    state = next((s for r, s in run_states.items() if s.get("current_agent") == agent_id), {})
    return {"agentId": agent_id, "state": state or {"status": "idle"}}


@router.post("/runs/{run_id}/stop")
async def stop_run(run_id: str):
    """Cancel a running agent task"""
    if run_id in active_runs:
        active_runs[run_id].cancel()
        return {"status": "stopping", "runId": run_id}
    return JSONResponse(status_code=404, content={"error": "Run not found or already finished"})


# =============================================================================
# AG-UI Protocol Endpoints
# =============================================================================

@router.get("/agents")
async def list_agents():
    """List all available agents (AG-UI compatible)"""
    agents_list = registry.list_agents()
    return {
        "agents": [
            registry.get_agent_info(agent_id)
            for agent_id in agents_list
        ],
        "count": len(agents_list)
    }


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    agent_id_raw = agent_id.replace("-", "_")
    info = registry.get_agent_info(agent_id_raw)
    
    if not info:
        return JSONResponse(status_code=404, content={"error": f"Agent {agent_id} not found"})
    
    return info


@router.post("/agui")
@router.post("/team/chat")
async def agui_team_endpoint(input_data: RunAgentInput, request: Request):
    """
    AG-UI Protocol Team Orchestration Endpoint
    
    This is the main AG-UI endpoint that:
    1. Accepts RunAgentInput with messages, tools, and context
    2. Streams AG-UI events (RUN_STARTED, STEP_*, TEXT_MESSAGE_*, etc.)
    3. Returns streaming response compatible with AG-UI clients
    """
    # Input validation per AG-UI best practices
    if not input_data.messages:
        return JSONResponse(
            status_code=400,
            content={"error": "messages required", "code": "INVALID_INPUT"}
        )
    
    accept_header = request.headers.get("accept", "text/event-stream")
    encoder = EventEncoder(accept=accept_header)
    
    async def event_generator():
        try:
            # 1. RUN_STARTED
            yield encoder.encode(RunStartedEvent(
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            ))
            
            # 2. Initial STATE_SNAPSHOT
            initial_state = {
                "status": "planning",
                "agents": [],
                "current_agent": None,
                "risk_level": "none"
            }
            run_states[input_data.run_id] = initial_state
            yield encoder.encode(StateSnapshotEvent(snapshot=initial_state))
            
            # 2.5: MESSAGES_SNAPSHOT
            yield encoder.encode(MessagesSnapshotEvent(
                messages=input_data.messages
            ))
            
            # 3. Extract task and context
            task = get_last_user_message(input_data.messages)
            context = build_context_dict(input_data)
            
            if not task:
                yield encoder.encode(TextMessageChunkEvent(
                    message_id=str(uuid.uuid4()),
                    delta="I didn't receive a message. How can I help you?"
                ))
                yield encoder.encode(RunFinishedEvent(
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id
                ))
                return
            
            # 4. Initialize team
            team = FlagPilotTeam(agents=input_data.agents)
            
            # 5. STEP_STARTED: Orchestrator Planning
            yield encoder.encode(StepStartedEvent(step_name="orchestrator-planning"))
            
            # 6. Run orchestration and stream results
            result = await team.run(task=task, context=context)
            
            yield encoder.encode(StepFinishedEvent(step_name="orchestrator-planning"))
            
            # 7. Update state with plan
            plan = result.get("orchestrator_analysis", {})
            patch = [
                {"op": "replace", "path": "/status", "value": "executing"},
                {"op": "add", "path": "/plan", "value": plan}
            ]
            run_states[input_data.run_id].update({"status": "executing", "plan": plan})
            yield encoder.encode(StateDeltaEvent(delta=patch))
            
            # 8. Stream agent outputs as STEP events with Activity tracking
            agent_outputs = result.get("agent_outputs", {})
            total_agents = len(agent_outputs)
            for idx, (agent_id, output) in enumerate(agent_outputs.items()):
                yield encoder.encode(StepStartedEvent(step_name=agent_id))
                
                # Activity event for progress visualization
                yield encoder.encode(ActivitySnapshotEvent(
                    message_id=f"activity-{agent_id}",
                    activity_type="AGENT_EXECUTION",
                    content={
                        "agent_id": agent_id,
                        "status": "running",
                        "progress": int((idx + 1) / total_agents * 100) if total_agents > 0 else 100,
                        "current_step": idx + 1,
                        "total_steps": total_agents
                    }
                ))
                
                # State update: current agent
                run_states[input_data.run_id]["current_agent"] = agent_id
                yield encoder.encode(StateDeltaEvent(delta=[
                    {"op": "replace", "path": "/current_agent", "value": agent_id}
                ]))
                
                # Stream agent output as text message
                msg_id = str(uuid.uuid4())
                yield encoder.encode(TextMessageStartEvent(message_id=msg_id))
                
                # Stream content (in chunks if large)
                content = str(output)
                chunk_size = 100
                for i in range(0, len(content), chunk_size):
                    yield encoder.encode(TextMessageContentEvent(
                        message_id=msg_id,
                        delta=content[i:i+chunk_size]
                    ))
                
                yield encoder.encode(TextMessageEndEvent(message_id=msg_id))
                yield encoder.encode(StepFinishedEvent(step_name=agent_id))
            
            # 9. Final synthesis
            synthesis = result.get("final_synthesis", "")
            if synthesis:
                yield encoder.encode(StepStartedEvent(step_name="synthesis"))
                
                synth_msg_id = str(uuid.uuid4())
                yield encoder.encode(TextMessageStartEvent(message_id=synth_msg_id))
                
                # Stream synthesis
                for i in range(0, len(synthesis), 100):
                    yield encoder.encode(TextMessageContentEvent(
                        message_id=synth_msg_id,
                        delta=synthesis[i:i+100]
                    ))
                
                yield encoder.encode(TextMessageEndEvent(message_id=synth_msg_id))
                yield encoder.encode(StepFinishedEvent(step_name="synthesis"))
            
            # 10. Final state
            risk_level = str(result.get("risk_level", "none")).lower()
            final_snapshot = {
                "status": "complete",
                "current_agent": None,
                "risk_level": risk_level
            }
            run_states[input_data.run_id] = final_snapshot
            yield encoder.encode(StateSnapshotEvent(snapshot=final_snapshot))
            
            # 11. RUN_FINISHED
            yield encoder.encode(RunFinishedEvent(
                thread_id=input_data.thread_id,
                run_id=input_data.run_id,
                result={"status": result.get("status", "COMPLETED")}
            ))
            
        except asyncio.CancelledError:
            logger.info(f"Run {input_data.run_id} cancelled")
            yield encoder.encode(RunFinishedEvent(
                thread_id=input_data.thread_id,
                run_id=input_data.run_id,
                result={"status": "cancelled"}
            ))
        except Exception as e:
            logger.exception(f"AG-UI endpoint error: {e}")
            yield encoder.encode(RunErrorEvent(
                message=str(e),
                code=type(e).__name__
            ))
        finally:
            active_runs.pop(input_data.run_id, None)

    # Wrap the generator in a task to allow cancellation via /stop
    task = asyncio.create_task(asyncio.sleep(0)) # Placeholder
    # We need a way to wrap the StreamingResponse's generator
    # For simplicity, we just use the generator directly in StreamingResponse
    # but we track the request if possible. 
    # Actually, we can just use the RunID to track the generation process.
    
    # Redefine generator to track itself
    async def tracked_event_generator():
        current_task = asyncio.current_task()
        active_runs[input_data.run_id] = current_task
        async for e in event_generator():
            yield e
    
    return StreamingResponse(
        tracked_event_generator(),
        media_type=encoder.get_content_type(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/agents/{agent_id}/chat")
async def agui_single_agent_endpoint(agent_id: str, input_data: RunAgentInput, request: Request):
    """
    AG-UI Protocol Single Agent Endpoint
    """
    agent_cls = registry.get_agent_class(agent_id)
    if not agent_cls:
        accept_header = request.headers.get("accept", "text/event-stream")
        encoder = EventEncoder(accept=accept_header)
        
        async def error_gen():
            yield encoder.encode(RunStartedEvent(thread_id=input_data.thread_id, run_id=input_data.run_id))
            yield encoder.encode(RunErrorEvent(
                message=f"Agent '{agent_id}' not found.",
                code="AGENT_NOT_FOUND"
            ))
        
        return StreamingResponse(error_gen(), media_type="text/event-stream")
    
    accept_header = request.headers.get("accept", "text/event-stream")
    encoder = EventEncoder(accept=accept_header)
    agent = agent_cls()
    
    async def event_generator():
        try:
            active_runs[input_data.run_id] = asyncio.current_task()
            
            yield encoder.encode(RunStartedEvent(thread_id=input_data.thread_id, run_id=input_data.run_id))
            yield encoder.encode(StepStartedEvent(step_name=agent_id))
            
            task = get_last_user_message(input_data.messages)
            context = build_context_dict(input_data)
            
            msg_id = str(uuid.uuid4())
            yield encoder.encode(TextMessageStartEvent(message_id=msg_id))
            
            if hasattr(agent, 'analyze_streaming'):
                async for event in agent.analyze_streaming(task, context):
                    if event.get("type") == "TEXT_MESSAGE_CONTENT":
                        yield encoder.encode(TextMessageContentEvent(
                            message_id=msg_id,
                            delta=event.get("delta", "")
                        ))
                    elif event.get("type") == "TEXT_MESSAGE_CHUNK":
                        yield encoder.encode(TextMessageContentEvent(
                            message_id=msg_id,
                            delta=event.get("delta", "")
                        ))
                    elif event.get("type") == "CUSTOM":
                        yield encoder.encode(CustomEvent(
                            name=event.get("name"),
                            value=event.get("value")
                        ))
            else:
                result = await agent.analyze(task, context)
                for i in range(0, len(result), 100):
                    yield encoder.encode(TextMessageContentEvent(
                        message_id=msg_id,
                        delta=result[i:i+100]
                    ))
            
            yield encoder.encode(TextMessageEndEvent(message_id=msg_id))
            yield encoder.encode(StepFinishedEvent(step_name=agent_id))
            yield encoder.encode(RunFinishedEvent(
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            ))
            
        except asyncio.CancelledError:
            yield encoder.encode(RunFinishedEvent(
                thread_id=input_data.thread_id,
                run_id=input_data.run_id,
                result={"status": "cancelled"}
            ))
        except Exception as e:
            logger.exception(f"Agent {agent_id} error: {e}")
            yield encoder.encode(RunErrorEvent(message=str(e), code=type(e).__name__))
        finally:
            active_runs.pop(input_data.run_id, None)
    
    return StreamingResponse(
        event_generator(),
        media_type=encoder.get_content_type(),
        headers={"Cache-Control": "no-cache"}
    )
