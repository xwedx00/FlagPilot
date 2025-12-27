"""
CopilotKit Integration for FlagPilot
=====================================
Provides AG-UI protocol integration with LangGraph agents.

Exports:
- flagpilot_agent: The main LangGraph agent for CopilotKit
- graph: The compiled LangGraph workflow
"""

from .sdk import flagpilot_agent
from .graph import graph

__all__ = ["flagpilot_agent", "graph"]
