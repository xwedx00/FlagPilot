"""
AI SDK v6 Compatible Streaming Protocol Formatter

Implements the UI Message Stream Protocol for Vercel AI SDK v5/v6.

IMPORTANT: AI SDK v6 has strict type validation:
- Standard types: text-start, text-delta, text-end, start, finish, error
- Custom data types MUST start with "data-" prefix
- All text events require an "id" field

Reference: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol
"""

import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime


class AISDKv6Formatter:
    """
    Format events for Vercel AI SDK v6 UI Message Stream.
    
    The stream uses Server-Sent Events (SSE) format with typed events.
    Custom data types MUST use the "data-{name}" format.
    """
    
    _current_message_id: Optional[str] = None
    
    @classmethod
    def _ensure_message_id(cls) -> str:
        """Ensure we have a message ID, create one if needed"""
        if cls._current_message_id is None:
            cls._current_message_id = str(uuid.uuid4())
        return cls._current_message_id
    
    @classmethod
    def _reset_message_id(cls):
        """Reset message ID for new messages"""
        cls._current_message_id = None
    
    @staticmethod
    def _sse_data(data: Any) -> str:
        """Format as SSE data event"""
        json_data = json.dumps(data) if not isinstance(data, str) else data
        return f"data: {json_data}\n\n"
    
    @classmethod
    def start(cls) -> str:
        """Start the stream - required first event"""
        cls._reset_message_id()
        msg_id = cls._ensure_message_id()
        return cls._sse_data({
            "type": "start",
            "messageId": msg_id,
        })
    
    @classmethod
    def text_start(cls) -> str:
        """Start a new text block"""
        return cls._sse_data({
            "type": "text-start",
            "id": cls._ensure_message_id(),
        })
    
    @classmethod
    def text_delta(cls, delta: str) -> str:
        """Send incremental text content"""
        return cls._sse_data({
            "type": "text-delta",
            "id": cls._ensure_message_id(),
            "delta": delta,
        })
    
    @classmethod
    def text_end(cls) -> str:
        """End the current text block"""
        return cls._sse_data({
            "type": "text-end",
            "id": cls._ensure_message_id(),
        })
    
    @classmethod
    def error(cls, message: str) -> str:
        """Send error event"""
        return cls._sse_data({
            "type": "error",
            "errorText": message,  # AI SDK v6 uses errorText, not error
        })
    
    @classmethod
    def finish(cls, reason: str = "stop") -> str:
        """Mark stream as complete"""
        result = cls._sse_data({
            "type": "finish",
            "finishReason": reason,
        })
        cls._reset_message_id()
        return result
    
    @classmethod
    def done(cls) -> str:
        """Alternative finish marker - [DONE]"""
        cls._reset_message_id()
        return "data: [DONE]\n\n"
    
    # === Custom data events (must use data- prefix) ===
    
    @classmethod
    def custom_data(cls, event_name: str, payload: Dict[str, Any]) -> str:
        """
        Send custom data event. 
        Type will be automatically prefixed with 'data-' if needed.
        """
        event_type = event_name if event_name.startswith("data-") else f"data-{event_name}"
        return cls._sse_data({
            "type": event_type,
            **payload
        })
    
    @classmethod
    def agent_status(cls, agent_id: str, status: str, action: Optional[str] = None) -> str:
        """Emit agent status update as custom data event"""
        payload = {
            "agentId": agent_id,
            "status": status,
        }
        if action:
            payload["action"] = action
        return cls.custom_data("agent-status", payload)
    
    @classmethod
    def workflow_update(cls, nodes: List[Dict] = None, edges: List[Dict] = None, **kwargs) -> str:
        """Emit workflow DAG update"""
        return cls.custom_data("workflow-update", {
            "nodes": nodes or [],
            "edges": edges or [],
        })
    
    @classmethod
    def workflow_complete(cls, workflow_id: str) -> str:
        """Emit workflow completion"""
        return cls.custom_data("workflow-complete", {
            "workflowId": workflow_id,
        })
    
    @classmethod
    def ui_component(cls, component_name: str, props: Dict[str, Any]) -> str:
        """Emit UI component"""
        return cls.custom_data("ui-component", {
            "componentName": component_name,
            "props": props,
        })


class VercelStreamFormatterV6:
    """
    Drop-in replacement for old VercelStreamFormatter.
    Converts old API to new AI SDK v6 format.
    """
    
    _started = False
    _text_started = False
    
    @classmethod
    def _ensure_started(cls) -> str:
        """Ensure stream has been started"""
        if not cls._started:
            cls._started = True
            cls._text_started = False
            return AISDKv6Formatter.start()
        return ""
    
    @classmethod
    def _ensure_text_started(cls) -> str:
        """Ensure text block has been started"""
        prefix = cls._ensure_started()
        if not cls._text_started:
            cls._text_started = True
            return prefix + AISDKv6Formatter.text_start()
        return prefix
    
    @classmethod
    def text(cls, content: str) -> str:
        """Format text chunk - converts to text-delta"""
        prefix = cls._ensure_text_started()
        return prefix + AISDKv6Formatter.text_delta(content)
    
    @classmethod
    def data(cls, payload) -> str:
        """Format custom data event - ignored for now as AI SDK v6 is strict"""
        # Custom data events cause validation errors, skip them
        # Just emit as a comment for debugging
        return ""
    
    @classmethod
    def error(cls, message: str) -> str:
        """Format error event"""
        cls._ensure_started()
        return AISDKv6Formatter.error(message)
    
    @classmethod
    def finish(cls, reason: str = "stop") -> str:
        """Format finish event"""
        prefix = ""
        if cls._text_started:
            prefix = AISDKv6Formatter.text_end()
            cls._text_started = False
        result = prefix + AISDKv6Formatter.finish(reason)
        cls._started = False
        return result
    
    @classmethod
    def agent_status(cls, agent_id: str, status: str, action: str = None) -> str:
        """Emit agent status - skip for now as it causes validation errors"""
        # Return empty - AI SDK v6 is too strict for custom events
        return ""
    
    @classmethod
    def workflow_update(cls, nodes: List[Dict] = None, edges: List[Dict] = None, **kwargs) -> str:
        """Emit workflow DAG update - skip for now"""
        return ""
    
    @classmethod
    def workflow_complete(cls, workflow_id: str) -> str:
        """Emit workflow completion - skip for now"""
        return ""
    
    @classmethod
    def message(cls, content: str, agent_id: str = None) -> str:
        """Emit chat message (uses text format)"""
        return cls.text(content)
    
    @classmethod
    def ui_component(cls, component_name: str, props: Dict[str, Any]) -> str:
        """Emit UI component - skip for now"""
        return ""


# Aliases
V6 = AISDKv6Formatter
VSF_V6 = VercelStreamFormatterV6
