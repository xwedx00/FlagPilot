"""
SSE Streaming Router for Real-Time Agent Updates
================================================
Provides Server-Sent Events (SSE) for the frontend to receive
real-time updates about agent activities, workflow changes, and results.

Supports two streaming formats:
1. Vercel AI SDK Data Stream Protocol (for useChat hook)
2. Standard SSE (for EventSource)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import asyncio
import json
import uuid
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from lib.database import get_session as get_db

# Import streaming formatters (both v1 and v6 for compatibility)
from stream.protocol import SSEFormatter as SSE, VercelStreamFormatter as VSF
from stream.protocol_v6 import VercelStreamFormatterV6 as VSF_V6, AISDKv6Formatter as V6
from dag import generate_workflow_plan, DAGExecutor, WorkflowPlan
from lib.context import current_user_id

router = APIRouter(prefix="/api/v1/stream", tags=["Streaming"])


class MissionRequest(BaseModel):
    """Request to start a new mission"""
    title: str
    description: str
    context: Optional[Dict[str, Any]] = None
    agents: Optional[List[str]] = None


class MissionResponse(BaseModel):
    """Response with mission ID"""
    id: str
    title: str
    status: str
    created_at: str


# Import centralized AGENT_ID_MAP from agents module
from agents import AGENT_REGISTRY, AGENT_ID_MAP, get_frontend_agent_id


def format_sse(event: str, data: Any) -> str:
    """Format data as SSE event"""
    json_data = json.dumps(data)
    return f"event: {event}\ndata: {json_data}\n\n"


async def stream_mission_events(
    mission_id: str,
    task: str,
    context: Optional[Dict[str, Any]],
    agents: Optional[List[str]]
) -> AsyncGenerator[str, None]:
    """
    Stream SSE events for a mission.
    
    Events:
    - connected: Initial connection confirmation
    - agent_status: Agent status changes (thinking, working, done)
    - agent_thinking: Agent thought process
    - workflow_update: DAG updates (nodes, edges)
    - message: Agent messages/results
    - ui_component: Generative UI component data
    - mission_complete: Mission finished
    """
    
    # Send connected event
    yield format_sse("connected", {
        "missionId": mission_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    await asyncio.sleep(0.1)
    
    try:
        # Try to import team orchestration - may fail due to pydantic issues
        # Strict MetaGPT Execution - No Fallback
        from agents import FlagPilotTeam
        
        # Phase 1: Orchestrator Start
        yield format_sse("agent_status", {
            "agentId": "flagpilot",
            "status": "working",
            "action": "Analyzing request..."
        })
        
        # Inject RAG Context if User ID is present
        if context:
            user_id = context.get("id")
            if user_id:
                try:
                    from ragflow.client import get_ragflow_client
                    rag_client = get_ragflow_client()
                    rag_context_str = await rag_client.get_agent_context(user_id, task)
                    if rag_context_str:
                        logger.info(f"Stream: Injected RAG context for user {user_id}")
                        context["RAG_CONTEXT"] = rag_context_str
                except Exception as e:
                    logger.warning(f"Stream: Failed to inject RAG context: {e}")
        
        # Initialize team
        team = FlagPilotTeam(agents=agents)
        
        # Step 1: Analyze
        orchestrator_plan = await team.orchestrator.analyze(task, context)
        
        yield format_sse("agent_thinking", {
            "agentId": "flagpilot",
            "thought": f"Plan: {orchestrator_plan[:100]}..."
        })
        
        yield format_sse("agent_status", {
            "agentId": "flagpilot",
            "status": "done",
            "action": "Plan created"
        })

        # Step 2: Identify Agents
        relevant_agents = team._identify_relevant_agents(task)
        # Use frontend ID map
        frontend_agents = [AGENT_ID_MAP.get(a, a) for a in relevant_agents]
        
        # Phase 2: Workflow DAG Update
        # Create DAG nodes/edges based on relevant agents
        nodes = [
            {
                "id": "flagpilot",
                "type": "agent",
                "position": {"x": 300, "y": 50},
                "data": {"agentId": "flagpilot", "status": "done"}
            }
        ]
        edges = []
        
        for i, agent_id in enumerate(frontend_agents):
            x_pos = 100 + (i * 200) # Spacing
            nodes.append({
                "id": agent_id,
                "type": "agent",
                "position": {"x": x_pos, "y": 250},
                "data": {"agentId": agent_id, "status": "waiting"}
            })
            edges.append({
                "id": f"e-flagpilot-{agent_id}",
                "source": "flagpilot",
                "target": agent_id,
                "animated": True
            })
            
        yield format_sse("workflow_update", {
            "nodes": nodes,
            "edges": edges
        })
        
        yield format_sse("message", {
            "agentId": "flagpilot",
            "content": f"**Plan:** {orchestrator_plan}\n\nActivating squad: {', '.join([a.replace('-', ' ').title() for a in relevant_agents])}"
        })

        # Step 3: Run Agents Parallel
        agent_tasks = []
        agent_outputs = {}
        
        # Mark all as working
        for agent_id in frontend_agents:
            yield format_sse("agent_status", {
                "agentId": agent_id,
                "status": "working",
                "action": "Processing..."
            })
        
        # Define wrapper to run agent and capture result
        async def run_agent_wrapper(a_id, role_cls):
             try:
                 agent_role = role_cls()
                 res = await team._run_agent(a_id, agent_role, task, context)
                 return a_id, res
             except Exception as e:
                 return a_id, f"Error: {e}"

        # Launch tasks
        tasks = []
        for agent_id in relevant_agents:
             if agent_id in team.active_agents:
                 tasks.append(run_agent_wrapper(agent_id, team.active_agents[agent_id]))
        
        # Wait for results
        if tasks:
            results = await asyncio.gather(*tasks)
            for raw_agent_id, output in results:
                agent_outputs[raw_agent_id] = output
                frontend_id = AGENT_ID_MAP.get(raw_agent_id, raw_agent_id)
                
                yield format_sse("agent_status", {
                    "agentId": frontend_id,
                    "status": "done"
                })
                
                yield format_sse("message", {
                    "agentId": frontend_id,
                    "content": f"**Findings:**\n{output}"
                })

        # Step 4: Synthesize
        yield format_sse("agent_status", {
            "agentId": "flagpilot",
            "status": "working",
            "action": "Synthesizing results..."
        })
        
        final_synthesis = await team._synthesize_results(task, orchestrator_plan, agent_outputs)
        
        yield format_sse("message", {
            "agentId": "flagpilot",
            "content": f"## ✅ Mission Complete\n\n{final_synthesis}"
        })
        
        yield format_sse("agent_status", {
            "agentId": "flagpilot",
            "status": "done",
            "action": "Mission complete"
        })

        yield format_sse("mission_complete", {
            "missionId": mission_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        # MetaGPT is the ONLY LLM source - show error when unavailable
        logger.error(f"MetaGPT agent error: {e}")
        
        yield format_sse("message", {
            "agentId": "flagpilot",
            "content": "⚠️ **Agent System Unavailable**\n\nThe MetaGPT agent orchestration system encountered an error. This platform requires MetaGPT for all LLM operations.\n\n**Error:** " + str(e)[:200] + "\n\nPlease ensure MetaGPT is properly configured and try again."
        })
        yield format_sse("agent_status", {
            "agentId": "flagpilot",
            "status": "error",
            "action": "MetaGPT unavailable"
        })
        
        # Always send mission_complete so the stream ends properly
        yield format_sse("mission_complete", {
            "missionId": mission_id,
            "timestamp": datetime.utcnow().isoformat()
        })


@router.post("/mission", response_model=MissionResponse)
async def create_mission(request: MissionRequest):
    """Create a new mission"""
    mission_id = f"mission-{uuid.uuid4().hex[:8]}"
    
    return MissionResponse(
        id=mission_id,
        title=request.title,
        status="created",
        created_at=datetime.utcnow().isoformat()
    )


@router.get("/mission/{mission_id}")
async def stream_mission(
    mission_id: str,
    task: str = "Analyze this request",
    context: Optional[str] = None
):
    """
    Stream SSE events for a mission.
    """
    parsed_context = None
    if context:
        try:
            parsed_context = json.loads(context)
        except:
            parsed_context = {"raw": context}
    
    return StreamingResponse(
        stream_mission_events(mission_id, task, parsed_context, None),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# NOTE: /test and /test-llm bypass routes have been removed.
# ALL LLM calls must go through MetaGPT agents via /chat or /workflow endpoints.


# === DAG-based endpoints ===

class WorkflowRequest(BaseModel):
    """Request to start a DAG-based workflow"""
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: str = "anonymous"


@router.post("/workflow")
async def stream_workflow(request: WorkflowRequest):
    """
    Start a DAG-based workflow with streaming.
    """
    
    async def generate():
        try:
            # --- RATE LIMIT CHECK ---
            if request.user_id and request.user_id != "anonymous":
                try:
                    from lib.rate_limit import RateLimiter
                    # Raises 429 if exceeded
                    await RateLimiter.check_rate_limit(request.user_id)
                except Exception as e:
                     logger.warning(f"Rate Limit Stop: {e}")
                     yield VSF.error("Rate limit exceeded. Please wait.")
                     yield VSF.finish("error")
                     return
            # ------------------------

            # --- CREDIT CHECK (INITIAL) ---
            if request.user_id and request.user_id != "anonymous":
                 try:
                     from lib.credits import CreditService
                     
                     # 1. Set Context for deep billing
                     token = current_user_id.set(request.user_id)
                     
                     # 2. Check Balance (No deduction yet, just ensure > 0)
                     from models.base import get_db as get_domain_db
                     async for db in get_domain_db():
                         has_credits = await CreditService.check_balance(db, request.user_id, 1)
                         if not has_credits:
                             yield VSF.error("Insufficient Credits. Please recharge.")
                             yield VSF.finish("error")
                             return
                         break
                 except Exception as e:
                     logger.error(f"Credit Check Error: {e}")
            # --------------------

            yield VSF_V6.agent_status("flagpilot", "thinking", "Planning workflow...")
            
            # Inject RAG Context if User ID is present
            if request.context:
                user_id = request.context.get("id") or request.user_id
                if user_id and user_id != "anonymous":
                    try:
                        from ragflow.client import get_ragflow_client
                        rag_client = get_ragflow_client()
                        rag_context_str = await rag_client.get_agent_context(user_id, request.message)
                        if rag_context_str:
                            logger.info(f"Stream: Injected RAG context for user {user_id}")
                            request.context["RAG_CONTEXT"] = rag_context_str
                            yield VSF_V6.agent_status("flagpilot", "thinking", "Analyzing knowledge base...")
                    except Exception as e:
                        logger.warning(f"Stream: Failed to inject RAG context: {e}")

            yield VSF_V6.text(f"🎯 **Planning your mission...**\n\n")
            
            plan = await generate_workflow_plan(
                user_request=request.message,
                context=request.context,
            )
            
            # --- FAST PATH: DIRECT RESPONSE ---
            if plan.outcome == "direct_response":
                yield VSF_V6.text(f"\n{plan.direct_response_content}\n")
                yield VSF_V6.agent_status("flagpilot", "done", "Responded directly")
                
                # PERSIST DIRECT RESPONSE
                try:
                    from models.base import get_db as get_domain_db
                    from models.intelligence import Mission, MissionStatus, ChatMessage
                    import uuid
                    
                    mission_id = request.context.get("mission_id") if request.context else None
                    
                    async for db in get_domain_db():
                        # 1. Create Mission if needed
                        if not mission_id:
                            new_mission = Mission(
                                user_id=request.user_id if request.user_id != "anonymous" else None,
                                title=request.message[:50],
                                status=MissionStatus.ACTIVE.value
                            )
                            db.add(new_mission)
                            await db.commit()
                            await db.refresh(new_mission)
                            mission_id = str(new_mission.id)
                        
                        # 2. Save User Message
                        user_msg = ChatMessage(
                            mission_id=uuid.UUID(mission_id),
                            role="user",
                            content=request.message
                        )
                        db.add(user_msg)

                        # 3. Save Assistant Message
                        ai_msg = ChatMessage(
                            mission_id=uuid.UUID(mission_id),
                            role="assistant",
                            agent_id="flagpilot",
                            content=plan.direct_response_content
                        )
                        db.add(ai_msg)
                        
                        await db.commit()
                        break
                except Exception as e:
                    logger.error(f"Persistence (Direct Response) Failed: {e}")

                yield VSF_V6.finish("stop")
                return # Exit generator
            # ----------------------------------
            
            yield VSF_V6.workflow_update(**plan.to_react_flow())
            yield VSF_V6.text(f"📋 Created workflow **{plan.id}** with {len(plan.nodes)} tasks:\n\n")
            
            for node in plan.nodes:
                yield VSF_V6.text(f"- **{node.agent}**: {node.instruction[:60]}...\n")
            
            yield VSF_V6.text(f"\n")
            yield VSF_V6.agent_status("flagpilot", "done", "Plan ready")
            
            # --- PERSISTENCE START ---
            execution_id = None
            try:
                from models.base import get_db as get_domain_db
                from models.intelligence import WorkflowExecution
                
                # We need to manually manage session here because we are in a generator
                async for db in get_domain_db():
                    # Create execution record
                    exec_record = WorkflowExecution(
                        user_id=request.user_id,
                        plan_snapshot=plan.model_dump(),
                        status="running"
                    )
                    db.add(exec_record)
                    await db.commit()
                    await db.refresh(exec_record)
                    execution_id = exec_record.id
                    yield VSF_V6.text(f"\n*Persistence: Execution ID {execution_id} created.*\n")
                    break # Get session and exit generator, but we need to keep session? 
                    # Actually get_db yields and then closes on exit.
                    # So we cannot easily keep it open across the long streaming yield.
                    # Strategy: Create record, close session. Update record later.
            except Exception as db_e:
                logger.error(f"Persistence Init Failed: {db_e}")
            # -------------------------

            # --- PERSISTENCE: MISSION & CHAT ---
            mission_id = request.context.get("mission_id") if request.context else None
            
            try:
                from models.base import get_db as get_domain_db
                from models.intelligence import Mission, MissionStatus, ChatMessage
                import uuid
                
                async for db in get_domain_db():
                    # 1. Create Mission if needed
                    if not mission_id:
                        new_mission = Mission(
                            user_id=request.user_id if request.user_id != "anonymous" else None, # Support auth
                            title=request.message[:50],
                            status=MissionStatus.ACTIVE.value
                        )
                        db.add(new_mission)
                        await db.commit()
                        await db.refresh(new_mission)
                        mission_id = str(new_mission.id)
                        # yield VSF_V6.text(f"DEBUG: Created mission {mission_id}\n")

                    # 2. Save User Message
                    user_msg = ChatMessage(
                        mission_id=uuid.UUID(mission_id),
                        role="user",
                        content=request.message
                    )
                    db.add(user_msg)
                    await db.commit()
                    break
            except Exception as e:
                logger.error(f"Mission Init Failed: {e}")
            # -----------------------------------

            executor = DAGExecutor()
            
            final_results = {}
            async for event in executor.execute(plan, request.user_id, request.context):
                event_type = event.get("type")
                
                if event_type == "agent_start":
                    yield VSF_V6.agent_status(event["agent"], "working", event.get("instruction", "")[:50])
                    yield VSF_V6.text(f"\n🤖 **{event['agent']}** working...\n")
                
                elif event_type == "agent_finish":
                    yield VSF_V6.agent_status(event["agent"], "done")
                    output = event.get("output", "")
                    if output:
                        yield VSF_V6.text(f"\n{output[:500]}\n")
                        final_results[event["agent"]] = output # Collect results
                        
                        # PERSIST AGENT MESSAGE
                        if mission_id:
                             try:
                                 async for db in get_domain_db():
                                     agent_msg = ChatMessage(
                                         mission_id=uuid.UUID(mission_id),
                                         role="assistant",
                                         agent_id=event["agent"],
                                         content=output
                                     )
                                     db.add(agent_msg)
                                     await db.commit()
                                     break
                             except Exception as e:
                                 logger.error(f"Failed to save agent msg: {e}")

                
                elif event_type == "agent_error":
                    yield VSF_V6.agent_status(event["agent"], "error")
                    yield VSF_V6.text(f"\n⚠️ **{event['agent']}** error: {event.get('error', 'Unknown')}\n")
                
                elif event_type == "workflow_update":
                    yield VSF_V6.workflow_update(event.get("nodes", []), event.get("edges", []))
                
                elif event_type == "ui_component":
                    yield VSF_V6.ui_component(event.get("componentName", ""), event.get("props", {}))
                
                elif event_type == "message":
                    content = event.get("content", "")
                    yield VSF_V6.message(content, event.get("agent"))
                    # PERSIST GENERAL MESSAGE
                    if mission_id and content:
                        try:
                            async for db in get_domain_db():
                                msg = ChatMessage(
                                    mission_id=uuid.UUID(mission_id),
                                    role="assistant",
                                    agent_id=event.get("agent", "flagpilot"),
                                    content=content
                                )
                                db.add(msg)
                                await db.commit()
                                break
                        except Exception as e:
                            logger.error(f"Failed to save msg: {e}")

                
                elif event_type == "workflow_complete":
                     # --- PERSISTENCE END ---
                    if execution_id:
                        try:
                             from models.base import get_db as get_domain_db
                             from models.intelligence import WorkflowExecution
                             from sqlalchemy import update
                             async for db in get_domain_db():
                                 stmt = (
                                     update(WorkflowExecution)
                                     .where(WorkflowExecution.id == execution_id)
                                     .values(
                                         status="completed",
                                         results=final_results,
                                         completed_at=datetime.utcnow()
                                     )
                                 )
                                 await db.execute(stmt)
                                 await db.commit()
                                 break
                        except Exception as db_e:
                            logger.error(f"Persistence Update Failed: {db_e}")
                    
                    # Reset Context
                    if 'token' in locals():
                        current_user_id.reset(token)
                    # -----------------------
                    # -----------------------
                    yield VSF_V6.text("\n\n✅ **Mission Complete!**\n")
                    yield VSF_V6.workflow_complete(plan.id)
            
            yield VSF_V6.finish("stop")
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            # Try to update status to failed
            if 'execution_id' in locals() and execution_id:
                 # ... (Omitted for brevity, but ideally we update on error too)
                 pass
            yield VSF_V6.error(str(e))
            yield VSF_V6.finish("error")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Vercel-AI-UI-Message-Stream": "v1",
        }
    )


@router.post("/workflow/plan")
async def generate_plan(request: WorkflowRequest):
    """
    Generate a workflow plan without executing it.
    """
    try:
        plan = await generate_workflow_plan(
            user_request=request.message,
            context=request.context,
        )
        
        return {
            "plan": plan.model_dump(),
            "react_flow": plan.to_react_flow(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ChatRequest(BaseModel):
    """Simple chat request"""
    message: str
    context: Optional[Dict[str, Any]] = None


@router.post("/chat")
async def stream_chat(request: ChatRequest):
    """
    Chat endpoint enforcing MetaGPT execution.
    Wraps the request as a workflow/mission to ensure agentic processing.
    """
    # Reuse stream_workflow logic for consistency
    return await stream_workflow(WorkflowRequest(
        message=request.message,
        context=request.context
    ))

@router.post("/workflow/{workflow_id}/run")
async def execute_saved_workflow(
    workflow_id: str,
    request: WorkflowRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a saved custom workflow.
    """
    from sqlalchemy import select
    from models.intelligence import Workflow
    
    # Fetch workflow
    query = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    async def generate():
        try:
            # --- RATE LIMIT CHECK ---
            if request.user_id and request.user_id != "anonymous":
                try:
                    from lib.rate_limit import RateLimiter
                    # Raises 429 if exceeded
                    await RateLimiter.check_rate_limit(request.user_id)
                except Exception as e:
                     logger.warning(f"Rate Limit Stop: {e}")
                     yield VSF.error("Rate limit exceeded. Please wait.")
                     yield VSF.finish("error")
                     return
            # ------------------------

            # --- CREDIT CHECK (INITIAL) ---
            if request.user_id and request.user_id != "anonymous":
                 try:
                     from lib.credits import CreditService
                     
                     # 1. Set Context
                     token = current_user_id.set(request.user_id)
                     
                     # 2. Check Balance
                     from models.base import get_db as get_domain_db
                     async for db_session in get_domain_db():
                         has_credits = await CreditService.check_balance(db_session, request.user_id, 1)
                         if not has_credits:
                             yield VSF.error("Insufficient Credits. Please recharge.")
                             yield VSF.finish("error")
                             return
                         break
                 except Exception as e:
                     logger.error(f"Credit Check Error: {e}")
            # --------------------

            yield VSF.agent_status("flagpilot", "thinking", f"Loading workflow: {workflow.name}...")
            yield VSF.text(f"🚀 **Executing Workflow: {workflow.name}**\n\n{workflow.description or ''}\n\n")
            
            # Convert JSON definition to WorkflowPlan
            # Assuming definition is compatible with WorkflowPlan
            try:
                # If definition is a dict, use parse_obj (v1) or model_validate (v2)
                # Since we are using Pydantic v2 now:
                plan = WorkflowPlan.model_validate(workflow.definition)
            except Exception as e:
                # Fallback: if definition is raw React Flow, we might need conversion
                # For now assume it is WorkflowPlan structure
                yield VSF.error(f"Invalid workflow definition: {e}")
                yield VSF.finish("error")
                return

            yield VSF.workflow_update(**plan.to_react_flow())
            
            executor = DAGExecutor()
            
            async for event in executor.execute(plan, request.user_id, request.context):
                event_type = event.get("type")
                
                if event_type == "agent_start":
                    yield VSF.agent_status(event["agent"], "working", event.get("instruction", "")[:50])
                    yield VSF.text(f"\n🤖 **{event['agent']}** working...\n")
                
                elif event_type == "agent_finish":
                    yield VSF.agent_status(event["agent"], "done")
                    output = event.get("output", "")
                    if output:
                        yield VSF.text(f"\n{output[:500]}\n")
                
                elif event_type == "agent_error":
                    yield VSF.agent_status(event["agent"], "error")
                    yield VSF.text(f"\n⚠️ **{event['agent']}** error: {event.get('error', 'Unknown')}\n")
                
                elif event_type == "workflow_update":
                    yield VSF.workflow_update(event.get("nodes", []), event.get("edges", []))
                
                elif event_type == "ui_component":
                    yield VSF.ui_component(event.get("componentName", ""), event.get("props", {}))
                
                elif event_type == "message":
                    yield VSF.message(event.get("content", ""), event.get("agent"))
                
                elif event_type == "workflow_complete":
                    yield VSF.text("\n\n✅ **Workflow Complete!**\n")
                    yield VSF.workflow_complete(plan.id)
            
            yield VSF.finish("stop")
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            yield VSF.error(str(e))
            yield VSF.finish("error")

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Vercel-AI-Data-Stream": "v1",
        }
    )
