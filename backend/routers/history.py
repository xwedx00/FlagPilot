"""
Workflow History Router
Allows users to retrieve past workflow execution results.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

from models.base import get_db
from models.intelligence import WorkflowExecution
from auth import verify_token, UserData

router = APIRouter(prefix="/api/v1/history", tags=["History"])

class WorkflowExecutionResponse(BaseModel):
    id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    plan_snapshot: Dict[str, Any]
    results: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True
    
    # Validator to convert UUID to string
    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=obj.user_id,
            status=obj.status,
            created_at=obj.created_at,
            completed_at=obj.completed_at,
            plan_snapshot=obj.plan_snapshot,
            results=obj.results
        )

@router.get("/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(execution_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific workflow execution result"""
    try:
        from uuid import UUID
        uuid_id = UUID(execution_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    query = select(WorkflowExecution).where(WorkflowExecution.id == uuid_id)
    result = await db.execute(query)
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    return WorkflowExecutionResponse.from_orm_model(execution)

@router.get("/user/{user_id}", response_model=List[WorkflowExecutionResponse])
async def get_user_history(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all workflow executions for a user"""
    query = (
        select(WorkflowExecution)
        .where(WorkflowExecution.user_id == user_id)
        .order_by(desc(WorkflowExecution.created_at))
        .limit(50)
    )
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return [WorkflowExecutionResponse.from_orm_model(e) for e in executions]


@router.get("/user/current", response_model=List[WorkflowExecutionResponse])
async def get_current_user_history(
    user: UserData = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all workflow executions for the current authenticated user"""
    query = (
        select(WorkflowExecution)
        .where(WorkflowExecution.user_id == user.id)
        .order_by(desc(WorkflowExecution.created_at))
        .limit(50)
    )
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return [WorkflowExecutionResponse.from_orm_model(e) for e in executions]

