import pytest
import asyncio
from dag.generator import generate_workflow_plan

@pytest.mark.asyncio
async def test_direct_response_trivial():
    """Test that a simple greeting triggers a Direct Response"""
    request = "Hi, I'm just looking around."
    plan = await generate_workflow_plan(request)
    
    # Assertions for Fast Path
    assert plan.outcome == "direct_response"
    assert plan.direct_response_content is not None
    assert len(plan.nodes) == 0
    print(f"\n[Direct Response] Input: '{request}'\nOutput: {plan.direct_response_content}")

@pytest.mark.asyncio
async def test_plan_response_complex():
    """Test that a complex request triggers a proper DAG Plan"""
    request = "Analyze this contract for me. It looks suspicious."
    plan = await generate_workflow_plan(request)
    
    # Assertions for Slow Path
    assert plan.outcome == "plan"
    assert len(plan.nodes) > 0
    assert plan.nodes[0].agent is not None
    print(f"\n[Plan Response] Input: '{request}'\nNodes: {len(plan.nodes)}")
