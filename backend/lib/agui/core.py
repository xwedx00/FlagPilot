from enum import Enum
from typing import Optional, List, Any, Union, Literal, Dict, Annotated
from pydantic import BaseModel, Field, ConfigDict
import time

def to_camel(string: str) -> str:
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])

class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        arbitrary_types_allowed=True,
        extra='allow'
    )

# =============================================================================
# Core Types
# =============================================================================

class Role(str, Enum):
    DEVELOPER = "developer"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"
    ACTIVITY = "activity"

class BaseMessage(ConfiguredBaseModel):
    id: str
    role: str

class DeveloperMessage(BaseMessage):
    role: Literal["developer"] = "developer"
    content: str
    name: Optional[str] = None

class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"
    content: str
    name: Optional[str] = None

class TextInputContent(ConfiguredBaseModel):
    type: Literal["text"] = "text"
    text: str

class BinaryInputContent(ConfiguredBaseModel):
    type: Literal["binary"] = "binary"
    mime_type: str
    id: Optional[str] = None
    url: Optional[str] = None
    data: Optional[str] = None
    filename: Optional[str] = None

class UserMessage(BaseMessage):
    role: Literal["user"] = "user"
    content: Union[str, List[Union[TextInputContent, BinaryInputContent]]]
    name: Optional[str] = None

class FunctionCall(ConfiguredBaseModel):
    name: str
    arguments: str

class ToolCall(ConfiguredBaseModel):
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall

class AssistantMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

class ToolMessage(BaseMessage):
    role: Literal["tool"] = "tool"
    content: str
    tool_call_id: str
    error: Optional[str] = None

class ActivityMessage(BaseMessage):
    role: Literal["activity"] = "activity"
    activity_type: str
    content: Dict[str, Any]

Message = Annotated[
    Union[
        DeveloperMessage,
        SystemMessage,
        AssistantMessage,
        UserMessage,
        ToolMessage,
        ActivityMessage,
    ],
    Field(discriminator="role")
]

class Tool(ConfiguredBaseModel):
    name: str
    description: str
    parameters: Any  # JSON Schema

class Context(ConfiguredBaseModel):
    description: str
    value: str

class RunAgentInput(ConfiguredBaseModel):
    thread_id: str
    run_id: str
    parent_run_id: Optional[str] = None
    state: Any = None
    messages: List[Message] = []
    tools: List[Tool] = []
    context: List[Context] = []
    agents: Optional[List[str]] = None  # FlagPilot Extension
    forwarded_props: Any = None

# =============================================================================
# Events
# =============================================================================

class EventType(str, Enum):
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TEXT_MESSAGE_CHUNK = "TEXT_MESSAGE_CHUNK"  # Convenience
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"
    TOOL_CALL_CHUNK = "TOOL_CALL_CHUNK" # Convenience
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    ACTIVITY_SNAPSHOT = "ACTIVITY_SNAPSHOT"
    ACTIVITY_DELTA = "ACTIVITY_DELTA"
    RAW = "RAW"
    CUSTOM = "CUSTOM"
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"

class BaseEvent(ConfiguredBaseModel):
    type: EventType
    timestamp: Optional[int] = Field(default_factory=lambda: int(time.time() * 1000))
    raw_event: Optional[Any] = None

# Lifecycle Events
class RunStartedEvent(BaseEvent):
    type: Literal[EventType.RUN_STARTED] = EventType.RUN_STARTED
    thread_id: str
    run_id: str
    parent_run_id: Optional[str] = None
    input: Optional[RunAgentInput] = None

class RunFinishedEvent(BaseEvent):
    type: Literal[EventType.RUN_FINISHED] = EventType.RUN_FINISHED
    thread_id: str
    run_id: str
    result: Optional[Any] = None

class RunErrorEvent(BaseEvent):
    type: Literal[EventType.RUN_ERROR] = EventType.RUN_ERROR
    message: str
    code: Optional[str] = None

class StepStartedEvent(BaseEvent):
    type: Literal[EventType.STEP_STARTED] = EventType.STEP_STARTED
    step_name: str

class StepFinishedEvent(BaseEvent):
    type: Literal[EventType.STEP_FINISHED] = EventType.STEP_FINISHED
    step_name: str

# Text Message Events
class TextMessageStartEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_START] = EventType.TEXT_MESSAGE_START
    message_id: str
    role: Literal["assistant"] = "assistant"

class TextMessageContentEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_CONTENT] = EventType.TEXT_MESSAGE_CONTENT
    message_id: str
    delta: str

class TextMessageEndEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_END] = EventType.TEXT_MESSAGE_END
    message_id: str

class TextMessageChunkEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_CHUNK] = EventType.TEXT_MESSAGE_CHUNK
    message_id: Optional[str] = None
    role: Optional[Literal["assistant", "user", "system", "developer"]] = "assistant"
    delta: Optional[str] = None

# Tool Call Events
class ToolCallStartEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_START] = EventType.TOOL_CALL_START
    tool_call_id: str
    tool_call_name: str
    parent_message_id: Optional[str] = None

class ToolCallArgsEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_ARGS] = EventType.TOOL_CALL_ARGS
    tool_call_id: str
    delta: str

class ToolCallEndEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_END] = EventType.TOOL_CALL_END
    tool_call_id: str

class ToolCallResultEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_RESULT] = EventType.TOOL_CALL_RESULT
    message_id: str
    tool_call_id: str
    content: str
    role: Optional[Literal["tool"]] = "tool"

# State Management Events
class StateSnapshotEvent(BaseEvent):
    type: Literal[EventType.STATE_SNAPSHOT] = EventType.STATE_SNAPSHOT
    snapshot: Any

class StateDeltaEvent(BaseEvent):
    type: Literal[EventType.STATE_DELTA] = EventType.STATE_DELTA
    delta: List[Any]  # JSON Patch

class MessagesSnapshotEvent(BaseEvent):
    type: Literal[EventType.MESSAGES_SNAPSHOT] = EventType.MESSAGES_SNAPSHOT
    messages: List[Message]

class ActivitySnapshotEvent(BaseEvent):
    type: Literal[EventType.ACTIVITY_SNAPSHOT] = EventType.ACTIVITY_SNAPSHOT
    message_id: str
    activity_type: str
    content: Any
    replace: bool = True

class ActivityDeltaEvent(BaseEvent):
    type: Literal[EventType.ACTIVITY_DELTA] = EventType.ACTIVITY_DELTA
    message_id: str
    activity_type: str
    patch: List[Any]

# Special Events
class RawEvent(BaseEvent):
    type: Literal[EventType.RAW] = EventType.RAW
    event: Any
    source: Optional[str] = None

class CustomEvent(BaseEvent):
    type: Literal[EventType.CUSTOM] = EventType.CUSTOM
    name: str
    value: Any

Event = Annotated[
    Union[
        RunStartedEvent,
        RunFinishedEvent,
        RunErrorEvent,
        StepStartedEvent,
        StepFinishedEvent,
        TextMessageStartEvent,
        TextMessageContentEvent,
        TextMessageEndEvent,
        TextMessageChunkEvent,
        ToolCallStartEvent,
        ToolCallArgsEvent,
        ToolCallEndEvent,
        ToolCallResultEvent,
        StateSnapshotEvent,
        StateDeltaEvent,
        MessagesSnapshotEvent,
        ActivitySnapshotEvent,
        ActivityDeltaEvent,
        RawEvent,
        CustomEvent,
    ],
    Field(discriminator="type")
]
