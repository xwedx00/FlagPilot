import json
from typing import Dict, Any, Union
from pydantic import BaseModel
from .core import BaseEvent

class EventEncoder:
    """
    Encodes AG-UI events into SSE format.
    Format: data: {json-serialized event}\n\n
    """
    
    def __init__(self, accept: str = None):
        self.accept = accept or "text/event-stream"
    
    def encode(self, event: Union[BaseEvent, Dict[str, Any]]) -> str:
        """
        Encodes an event into a string representation.
        """
        # Convert Pydantic model to dict if needed
        if hasattr(event, "model_dump"):
            data = event.model_dump(exclude_none=True)
        elif isinstance(event, dict):
            data = event
        else:
            raise ValueError(f"Unsupported event type: {type(event)}")
            
        # Convert to camelCase for wire format
        wire_event = self._to_camel_case(data)
        json_data = json.dumps(wire_event)
        
        return f"data: {json_data}\n\n"
    
    def get_content_type(self) -> str:
        """Return the content type for the response"""
        return "text/event-stream"
    
    @staticmethod
    def _to_camel_case(data: Any) -> Any:
        """Convert dict keys from snake_case to camelCase recursively"""
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                # Convert key
                components = key.split('_')
                camel_key = components[0] + ''.join(x.title() for x in components[1:])
                # Recurse on value
                new_dict[camel_key] = EventEncoder._to_camel_case(value)
            return new_dict
        elif isinstance(data, list):
            return [EventEncoder._to_camel_case(item) for item in data]
        else:
            return data
