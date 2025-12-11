"""
Missions Router - Database-backed CRUD operations
=================================================
Provides endpoints for mission management with full PostgreSQL persistence.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import uuid
from loguru import logger

from models.base import get_db
from models.intelligence import Mission, MissionStatus, ChatMessage
from auth import get_current_user, UserData

router = APIRouter(prefix="/api/v1/missions", tags=["Missions"])


class MissionCreate(BaseModel):
    """Request to create a mission"""
    title: str
    description: Optional[str] = None
    project_id: Optional[str] = None


class MissionUpdate(BaseModel):
    """Request to update a mission"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class MessageResponse(BaseModel):
    """Chat message response"""
    id: str
    role: str
    content: str
    agent_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class MissionResponse(BaseModel):
    """Mission response model"""
    id: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    message_count: int = 0

    class Config:
        from_attributes = True


class MissionDetailResponse(MissionResponse):
    """Mission with messages"""
    messages: List[MessageResponse] = []


@router.post("", response_model=MissionResponse)
async def create_mission(
    request: MissionCreate,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new mission"""
    now = datetime.utcnow()
    
    mission = Mission(
        user_id=user.id,
        title=request.title,
        description=request.description,
        status=MissionStatus.ACTIVE.value,
        project_id=uuid.UUID(request.project_id) if request.project_id else None,
    )
    
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    
    logger.info(f"Created mission: {mission.id}")
    
    return MissionResponse(
        id=str(mission.id),
        title=mission.title,
        description=mission.description,
        status=mission.status,
        created_at=mission.created_at.isoformat(),
        updated_at=mission.updated_at.isoformat(),
        message_count=0,
    )


@router.get("", response_model=List[MissionResponse])
async def list_missions(
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """List all missions for the current user"""
    from sqlalchemy.orm import selectinload  # Eager-load to avoid lazy-load errors
    
    query = (
        select(Mission)
        .where(Mission.user_id == user.id)
        .options(selectinload(Mission.messages))  # Eager-load messages
        .order_by(Mission.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    missions = result.scalars().all()
    
    return [
        MissionResponse(
            id=str(m.id),
            title=m.title,
            description=m.description,
            status=m.status,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat(),
            message_count=len(m.messages) if m.messages else 0,
        )
        for m in missions
    ]


@router.get("/{mission_id}", response_model=MissionDetailResponse)
async def get_mission(
    mission_id: str,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific mission with all messages"""
    query = select(Mission).where(
        Mission.id == uuid.UUID(mission_id),
        Mission.user_id == user.id
    )
    result = await db.execute(query)
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return MissionDetailResponse(
        id=str(mission.id),
        title=mission.title,
        description=mission.description,
        status=mission.status,
        created_at=mission.created_at.isoformat(),
        updated_at=mission.updated_at.isoformat(),
        message_count=len(mission.messages) if mission.messages else 0,
        messages=[
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                agent_id=msg.agent_id,
                created_at=msg.created_at.isoformat(),
            )
            for msg in (mission.messages or [])
        ],
    )


@router.patch("/{mission_id}", response_model=MissionResponse)
async def update_mission(
    mission_id: str,
    request: MissionUpdate,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a mission"""
    query = select(Mission).where(
        Mission.id == uuid.UUID(mission_id),
        Mission.user_id == user.id
    )
    result = await db.execute(query)
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if request.title:
        mission.title = request.title
    if request.description is not None:
        mission.description = request.description
    if request.status:
        mission.status = request.status
    
    await db.commit()
    await db.refresh(mission)
    
    return MissionResponse(
        id=str(mission.id),
        title=mission.title,
        description=mission.description,
        status=mission.status,
        created_at=mission.created_at.isoformat(),
        updated_at=mission.updated_at.isoformat(),
        message_count=len(mission.messages) if mission.messages else 0,
    )


@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: str,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a mission and all its messages"""
    query = select(Mission).where(
        Mission.id == uuid.UUID(mission_id),
        Mission.user_id == user.id
    )
    result = await db.execute(query)
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    await db.delete(mission)
    await db.commit()
    
    logger.info(f"Deleted mission: {mission_id}")
    return {"deleted": True, "id": mission_id}


@router.get("/{mission_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    mission_id: str,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all messages for a mission"""
    # Verify mission access
    query = select(Mission).where(
        Mission.id == uuid.UUID(mission_id),
        Mission.user_id == user.id
    )
    result = await db.execute(query)
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Get messages
    msg_query = (
        select(ChatMessage)
        .where(ChatMessage.mission_id == uuid.UUID(mission_id))
        .order_by(ChatMessage.created_at.asc())
    )
    msg_result = await db.execute(msg_query)
    messages = msg_result.scalars().all()
    
    return [
        MessageResponse(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            agent_id=msg.agent_id,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]
