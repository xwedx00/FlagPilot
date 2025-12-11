"""
Workflow Templates Router
Allows users to create and save custom workflow templates.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from models.base import get_db
from auth import verify_token, UserData

router = APIRouter(prefix="/api/v1/workflows/templates", tags=["Workflow Templates"])


# =============================================================================
# Pydantic Models
# =============================================================================

class WorkflowNodeSchema(BaseModel):
    id: str
    agent: str
    instruction: str
    depends_on: Optional[List[str]] = None


class WorkflowEdgeSchema(BaseModel):
    source: str
    target: str


class CreateWorkflowTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNodeSchema]
    edges: List[WorkflowEdgeSchema] = []
    is_public: bool = False


class WorkflowTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    nodes: List[dict]
    edges: List[dict]
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_public: bool

    class Config:
        from_attributes = True


# =============================================================================
# In-Memory Store (Replace with DB in production)
# =============================================================================

# Simple in-memory storage for workflow templates
# In production, use a proper database table
_templates_store: dict = {}


# =============================================================================
# Endpoints
# =============================================================================

@router.get("", response_model=List[WorkflowTemplateResponse])
async def list_templates(
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """List all workflow templates for the current user"""
    user_templates = [
        t for t in _templates_store.values()
        if t["user_id"] == user.id or t["is_public"]
    ]
    return sorted(user_templates, key=lambda x: x["created_at"], reverse=True)


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
async def get_template(
    template_id: str,
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow template"""
    template = _templates_store.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template["user_id"] != user.id and not template["is_public"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return template


@router.post("", response_model=WorkflowTemplateResponse)
async def create_template(
    request: CreateWorkflowTemplateRequest,
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow template"""
    template_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    template = {
        "id": template_id,
        "name": request.name,
        "description": request.description,
        "nodes": [n.model_dump() for n in request.nodes],
        "edges": [e.model_dump() for e in request.edges],
        "user_id": user.id,
        "created_at": now,
        "updated_at": now,
        "is_public": request.is_public,
    }
    
    _templates_store[template_id] = template
    return template


@router.patch("/{template_id}", response_model=WorkflowTemplateResponse)
async def update_template(
    template_id: str,
    request: CreateWorkflowTemplateRequest,
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing workflow template"""
    template = _templates_store.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    template["name"] = request.name
    template["description"] = request.description
    template["nodes"] = [n.model_dump() for n in request.nodes]
    template["edges"] = [e.model_dump() for e in request.edges]
    template["is_public"] = request.is_public
    template["updated_at"] = datetime.utcnow()
    
    _templates_store[template_id] = template
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow template"""
    template = _templates_store.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    del _templates_store[template_id]
    return {"status": "deleted"}


@router.post("/{template_id}/execute")
async def execute_template(
    template_id: str,
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Execute a saved workflow template"""
    template = _templates_store.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template["user_id"] != user.id and not template["is_public"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create an execution ID - actual execution would go through the DAG executor
    execution_id = str(uuid.uuid4())
    
    # TODO: Integrate with the actual DAG executor to run the custom workflow
    # For now, return the execution ID which the frontend can use to track progress
    
    return {"executionId": execution_id, "status": "started"}
