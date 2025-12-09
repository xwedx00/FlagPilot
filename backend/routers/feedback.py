"""
Feedback Router for RLHF

Handles user feedback (thumbs up/down) to store successful workflows
in Global Wisdom for the learning loop.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from loguru import logger

from auth import get_current_user, UserData


router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    """User feedback on a workflow"""
    workflow_id: str
    rating: int  # 1-5 stars
    message_id: Optional[str] = None
    comment: Optional[str] = None
    workflow_type: Optional[str] = None
    agents_used: Optional[list] = None


class FeedbackResponse(BaseModel):
    """Feedback submission result"""
    success: bool
    stored_in_global_wisdom: bool
    message: str


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserData = Depends(get_current_user),
):
    """
    Submit feedback on a workflow.
    
    If rating >= 4, the workflow is considered successful and
    is stored in Global Wisdom for future reference.
    """
    try:
        stored = False
        
        if request.rating >= 4:
            # Store in Global Wisdom for RLHF
            stored = await store_in_global_wisdom(request)
        
        return FeedbackResponse(
            success=True,
            stored_in_global_wisdom=stored,
            message="Feedback received. Thank you!" if not stored 
                    else "Great! This workflow will help improve future suggestions."
        )
        
    except Exception as e:
        logger.error(f"Failed to process feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/thumbs-up/{workflow_id}")
async def thumbs_up(
    workflow_id: str,
    user: UserData = Depends(get_current_user),
):
    """Quick thumbs up for a workflow (rating = 5)"""
    return await submit_feedback(
        FeedbackRequest(workflow_id=workflow_id, rating=5),
        user
    )


@router.post("/thumbs-down/{workflow_id}")
async def thumbs_down(
    workflow_id: str,
    user: UserData = Depends(get_current_user),
):
    """Quick thumbs down for a workflow (rating = 1)"""
    return await submit_feedback(
        FeedbackRequest(workflow_id=workflow_id, rating=1),
        user
    )


async def store_in_global_wisdom(request: FeedbackRequest) -> bool:
    """
    Store a successful workflow in Global Wisdom.
    
    This anonymizes the workflow and stores it for future reference
    by the Manager Agent.
    """
    try:
        from ragflow import get_ragflow_client
        
        # Get the Ragflow client
        client = get_ragflow_client()
        
        # Create a summary of the workflow
        summary = f"""
        Workflow Type: {request.workflow_type or 'general'}
        Rating: {request.rating}/5
        Agents Used: {', '.join(request.agents_used or ['unknown'])}
        User Comment: {request.comment or 'No comment'}
        """
        
        # Add to Global Wisdom via Ragflow
        # Ragflow handles chunking and embeddings internally
        success = await client.add_successful_workflow(
            summary=summary,
            workflow_type=request.workflow_type or "general",
            agents_used=request.agents_used or [],
            rating=request.rating,
        )
        
        if success:
            logger.info(f"Stored workflow {request.workflow_id} in Global Wisdom (rating: {request.rating})")
            return True
        else:
            logger.warning(f"Failed to store workflow {request.workflow_id} in Global Wisdom")
            return False
        
    except Exception as e:
        logger.error(f"Failed to store in Global Wisdom: {e}")
        return False
