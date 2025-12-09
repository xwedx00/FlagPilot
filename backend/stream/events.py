"""
Stream Event Types and Schemas

Defines the event types used in streaming responses.
"""

from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class StreamEventType(str, Enum):
    """Types of events that can be streamed"""
    
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    
    # Agent events
    AGENT_STATUS = "agent_status"
    AGENT_THINKING = "agent_thinking"
    AGENT_OUTPUT = "agent_output"
    
    # Workflow events
    WORKFLOW_START = "workflow_start"
    WORKFLOW_UPDATE = "workflow_update"
    WORKFLOW_COMPLETE = "workflow_complete"
    
    # Message events
    MESSAGE = "message"
    MESSAGE_DELTA = "message_delta"
    
    # UI events
    UI_COMPONENT = "ui_component"
    ARTIFACT = "artifact"
    
    # Mission events
    MISSION_START = "mission_start"
    MISSION_COMPLETE = "mission_complete"


class AgentStatus(str, Enum):
    """Agent status states"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


class AgentStatusEvent(BaseModel):
    """Event for agent status updates"""
    type: str = StreamEventType.AGENT_STATUS
    agentId: str
    status: AgentStatus
    action: Optional[str] = None


class AgentThinkingEvent(BaseModel):
    """Event for agent thought process"""
    type: str = StreamEventType.AGENT_THINKING
    agentId: str
    thought: str


class WorkflowUpdateEvent(BaseModel):
    """Event for workflow DAG updates"""
    type: str = StreamEventType.WORKFLOW_UPDATE
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class UIComponentEvent(BaseModel):
    """Event for generative UI components"""
    type: str = StreamEventType.UI_COMPONENT
    componentName: str
    props: Dict[str, Any]


class MessageEvent(BaseModel):
    """Event for chat messages"""
    type: str = StreamEventType.MESSAGE
    content: str
    agentId: Optional[str] = None
