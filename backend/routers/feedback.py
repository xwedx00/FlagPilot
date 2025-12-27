
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from lib.auth.middleware import get_current_user
from lib.memory.manager import get_memory_manager
from loguru import logger

router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    task: str
    outcome: str
    lesson: str
    score: int  # 1 for Thumbs Up, -1 for Thumbs Down
    is_public: bool = True

@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Submit feedback for a job/hiring interaction.
    If positive, it saves the 'lesson learned' to the Experience Gallery.
    """
    try:
        logger.info(f"Received feedback from user {user_id} (Score: {request.score})")
        
        # Save to experience gallery
        memory = get_memory_manager()
        await memory.save_experience(
            user_id=user_id,
            task=request.task,
            outcome=request.outcome,
            lesson=request.lesson,
            score=request.score
        )
        
        return {"status": "success", "message": "Feedback recorded and stored in memory."}
        
    except Exception as e:
        logger.error(f"Failed to process feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
