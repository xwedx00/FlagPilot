"""
Streaming Protocol Formatters

Implements:
1. Vercel AI SDK Data Stream Protocol v1
2. Standard SSE (Server-Sent Events)

Reference: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol
"""

import json
from typing import Any, Dict, List, Union
from enum import Enum

from .events import StreamEventType, AgentStatus


class VercelStreamCode(str, Enum):
    """Vercel AI SDK Data Stream Protocol codes"""
    TEXT = "0"           # Text content for chat
    DATA = "2"           # Custom data (JSON array)
    ERROR = "3"          # Error message
    ASSISTANT_MSG = "8"  # Assistant message info
    TOOL_CALL = "9"      # Tool call
    TOOL_RESULT = "a"    # Tool result
    FINISH = "d"         # Finish message
    STEP_FINISH = "e"    # Step finish


class VercelStreamFormatter:
    """
    Format events for Vercel AI SDK Data Stream Protocol v1.
    
    Use with FastAPI StreamingResponse:
    
        async def generator():
            yield VSF.text("Hello ")
            yield VSF.text("world!")
            yield VSF.data({"type": "custom", "value": 123})
            yield VSF.finish()
        
        return StreamingResponse(generator(), media_type="text/plain")
    """
    
    @staticmethod
    def text(content: str) -> str:
        """
        Format a text chunk.
        Appears in the chat message bubble.
        
        Format: 0:"escaped text"\n
        """
        return f'{VercelStreamCode.TEXT.value}:{json.dumps(content)}\n'
    
    @staticmethod
    def data(payload: Union[Dict, List]) -> str:
        """
        Format a custom data event.
        Use for workflow updates, UI components, agent status, etc.
        
        Format: 2:[{json}]\n
        """
        # Data must be wrapped in array
        if isinstance(payload, dict):
            payload = [payload]
        return f'{VercelStreamCode.DATA.value}:{json.dumps(payload)}\n'
    
    @staticmethod
    def error(message: str) -> str:
        """
        Format an error event.
        
        Format: 3:"error message"\n
        """
        return f'{VercelStreamCode.ERROR.value}:{json.dumps(message)}\n'
    
    @staticmethod
    def tool_call(
        tool_call_id: str,
        tool_name: str,
        args: Dict[str, Any],
    ) -> str:
        """
        Format a tool call event.
        
        Format: 9:{toolCallId, toolName, args}\n
        """
        return f'{VercelStreamCode.TOOL_CALL.value}:{json.dumps({"toolCallId": tool_call_id, "toolName": tool_name, "args": args})}\n'
    
    @staticmethod
    def tool_result(
        tool_call_id: str,
        result: Any,
    ) -> str:
        """
        Format a tool result event.
        
        Format: a:{toolCallId, result}\n
        """
        return f'{VercelStreamCode.TOOL_RESULT.value}:{json.dumps({"toolCallId": tool_call_id, "result": result})}\n'
    
    @staticmethod
    def finish(reason: str = "stop") -> str:
        """
        Format a finish event.
        
        Format: d:{finishReason}\n
        """
        return f'{VercelStreamCode.FINISH.value}:{json.dumps({"finishReason": reason})}\n'
    
    # === FlagPilot-specific convenience methods ===
    
    @staticmethod
    def agent_status(
        agent_id: str, 
        status: Union[str, AgentStatus], 
        action: str = None
    ) -> str:
        """Emit agent status update"""
        payload = {
            "type": StreamEventType.AGENT_STATUS,
            "agentId": agent_id,
            "status": status.value if isinstance(status, AgentStatus) else status,
        }
        if action:
            payload["action"] = action
        return VercelStreamFormatter.data(payload)
    
    @staticmethod
    def agent_thinking(agent_id: str, thought: str) -> str:
        """Emit agent thinking event"""
        return VercelStreamFormatter.data({
            "type": StreamEventType.AGENT_THINKING,
            "agentId": agent_id,
            "thought": thought,
        })
    
    @staticmethod
    def workflow_update(nodes: List[Dict], edges: List[Dict]) -> str:
        """Emit workflow DAG update"""
        return VercelStreamFormatter.data({
            "type": StreamEventType.WORKFLOW_UPDATE,
            "nodes": nodes,
            "edges": edges,
        })
    
    @staticmethod
    def ui_component(component_name: str, props: Dict[str, Any]) -> str:
        """Emit generative UI component"""
        return VercelStreamFormatter.data({
            "type": StreamEventType.UI_COMPONENT,
            "componentName": component_name,
            "props": props,
        })
    
    @staticmethod
    def message(content: str, agent_id: str = None) -> str:
        """Emit chat message from agent"""
        payload = {
            "type": StreamEventType.MESSAGE,
            "content": content,
        }
        if agent_id:
            payload["agentId"] = agent_id
        return VercelStreamFormatter.data(payload)
    
    @staticmethod
    def workflow_complete(workflow_id: str, status: str = "completed") -> str:
        """Emit workflow completion event"""
        return VercelStreamFormatter.data({
            "type": StreamEventType.WORKFLOW_COMPLETE,
            "workflowId": workflow_id,
            "status": status,
        })


class SSEFormatter:
    """
    Format events as standard Server-Sent Events.
    
    Use when not using Vercel AI SDK on frontend:
    
        async def generator():
            yield SSE.event("connected", {"status": "ok"})
            yield SSE.event("message", {"text": "Hello"})
        
        return StreamingResponse(generator(), media_type="text/event-stream")
    """
    
    @staticmethod
    def event(event_type: str, data: Any) -> str:
        """
        Format an SSE event.
        
        Format:
            event: event_type
            data: json_data
            
        """
        json_data = json.dumps(data) if not isinstance(data, str) else data
        return f"event: {event_type}\ndata: {json_data}\n\n"
    
    @staticmethod
    def comment(text: str) -> str:
        """
        Format an SSE comment (for keep-alive).
        
        Format: : comment text\n\n
        """
        return f": {text}\n\n"
    
    @staticmethod
    def retry(milliseconds: int) -> str:
        """
        Set client retry interval.
        
        Format: retry: milliseconds\n\n
        """
        return f"retry: {milliseconds}\n\n"
    
    # === Convenience methods ===
    
    @staticmethod
    def agent_status(agent_id: str, status: str, action: str = None) -> str:
        payload = {"agentId": agent_id, "status": status}
        if action:
            payload["action"] = action
        return SSEFormatter.event("agent_status", payload)
    
    @staticmethod
    def agent_thinking(agent_id: str, thought: str) -> str:
        return SSEFormatter.event("agent_thinking", {
            "agentId": agent_id,
            "thought": thought,
        })
    
    @staticmethod
    def workflow_update(nodes: List[Dict], edges: List[Dict]) -> str:
        return SSEFormatter.event("workflow_update", {
            "nodes": nodes,
            "edges": edges,
        })
    
    @staticmethod
    def ui_component(component_name: str, props: Dict[str, Any]) -> str:
        return SSEFormatter.event("ui_component", {
            "componentName": component_name,
            "props": props,
        })
    
    @staticmethod
    def message(content: str, agent_id: str = None) -> str:
        payload = {"content": content}
        if agent_id:
            payload["agentId"] = agent_id
        return SSEFormatter.event("message", payload)
    
    @staticmethod
    def mission_complete(mission_id: str) -> str:
        return SSEFormatter.event("mission_complete", {"missionId": mission_id})


# Aliases for convenience
VSF = VercelStreamFormatter
SSE = SSEFormatter
