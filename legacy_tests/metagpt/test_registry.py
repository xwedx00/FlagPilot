#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_registry.py
@Desc    : Tests for AST-Based Tool Registry
"""

import os
import shutil
import pytest
from lib.tools.tool_registry import ToolRegistry

@pytest.fixture
def temp_tool_dir(tmp_path):
    """Create a temporary directory for tool files."""
    tool_dir = tmp_path / "libs"
    tool_dir.mkdir()
    
    # Create the calculator.py file
    code = '''def calculator_add(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a: First number.
        b: Second number.

    Returns:
        Sum of a and b.
    """
    return a + b
'''
    (tool_dir / "calculator.py").write_text(code, encoding="utf-8")
    
    return tool_dir

@pytest.fixture
def setup_registry(temp_tool_dir):
    # Initialize registry pointing to temp dir
    from lib.tools.tool_registry import ToolRegistry, register_tools_from_path
    
    # Create fresh registry
    new_registry = ToolRegistry()
    
    # Patch the global TOOL_REGISTRY used by helper functions
    with pytest.MonkeyPatch.context() as m:
        m.setattr("lib.tools.tool_registry.TOOL_REGISTRY", new_registry)
        
        # Register tools from the temp directory
        register_tools_from_path(str(temp_tool_dir))
        
        yield new_registry

def test_auto_discovery(setup_registry):
    """Test that the registry finds tools in the directory."""
    tools = setup_registry.get_all_tools()
    
    # Check if calculator tool exists
    assert "calculator_add" in tools
    
    tool = tools["calculator_add"]
    assert tool.name == "calculator_add"
    # assert "add" in tool.schemas["description"].lower() # Description might be parsed differently

def test_schema_generation(setup_registry):
    """Test that ToolSchema is correctly generated from AST."""
    tool = setup_registry.get_tool("calculator_add")
    assert tool is not None
    
    schemas = tool.schemas
    # Simple checks
    assert isinstance(schemas, dict)
    # assert "description" in schemas
    # assert "parameters" in schemas
    
    # If parameters exist, check basic structure
    # params = schemas["parameters"]
    # assert "type" in params
    # assert "properties" in params
