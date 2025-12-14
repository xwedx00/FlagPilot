from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from models.base import get_db
from models.intelligence import Mission, MissionStatus, ChatMessage
from auth import get_current_user, UserData

router = APIRouter(prefix="/api/missions", tags=["Missions"])

class ThreadCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ThreadUpdate(BaseModel):
    title: str

class ThreadResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[ThreadResponse])
async def list_threads(
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all threads for current user"""
    query = select(Mission).where(
        Mission.user_id == user.id,
        Mission.status == MissionStatus.ACTIVE.value
    ).order_by(Mission.updated_at.desc())
    result = await db.execute(query)
    missions = result.scalars().all()
    return missions

@router.post("", response_model=ThreadResponse)
async def create_thread(
    thread: ThreadCreate,
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new thread (or return existing if ID provided in future)"""
    # For now, standard creation
    new_mission = Mission(
        status=MissionStatus.ACTIVE.value,
        # id=... if we want client-generated IDs here, but usually POST is server-gen
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=user.id, # Ensure user_id is set
        title=thread.title
    )
    db.add(new_mission)
    await db.commit()
    await db.refresh(new_mission)
    return new_mission

@router.patch("/{mission_id}", response_model=ThreadResponse)
async def update_mission(mission_id: str, update_data: ThreadUpdate, session: AsyncSession = Depends(get_db)):
    """Update mission title"""
    try:
        mission_uuid = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID format")

    result = await session.execute(select(Mission).where(Mission.id == mission_uuid))
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if update_data.title is not None:
        mission.title = update_data.title
        mission.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(mission)
    return mission

@router.delete("/{mission_id}")
async def delete_mission(mission_id: str, session: AsyncSession = Depends(get_db)):
    """Delete a mission"""
    try:
        mission_uuid = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID format")

    result = await session.execute(select(Mission).where(Mission.id == mission_uuid))
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    await session.delete(mission)
    await session.commit()
    return {"status": "success", "id": mission_id}

@router.get("/{mission_id}/messages", response_model=List[MessageResponse])
async def get_mission_messages(mission_id: str, session: AsyncSession = Depends(get_db)):
    """Get all messages for a mission"""
    try:
        mission_uuid = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID format")

    # Verify mission exists
    result = await session.execute(select(Mission).where(Mission.id == mission_uuid))
    mission = result.scalar_one_or_none()
    if not mission:
        # If thread doesn't exist but ID is valid UUID, return empty messages
        # This allows frontend to optimistically route to new thread ID
        return []

    # Fetch messages
    query = select(ChatMessage).where(
        ChatMessage.mission_id == mission_uuid
    ).order_by(ChatMessage.created_at.asc())
    
    result = await session.execute(query)
    messages = result.scalars().all()
    return messages
