from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.status import StatusStory
from app.models.user import User
from app.schemas.all_schemas import StatusCreateRequest, StatusResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/statuses", tags=["Statuses"])

def format_status_dict(s: StatusStory, current_user_id: str) -> dict:
    return {
        "id": s.id,
        "userId": s.user_id,
        "userName": s.user_name,
        "userAvatar": s.user_avatar,
        "isMe": s.user_id == current_user_id,
        "hasUnseen": s.has_unseen,
        "timestamp": s.timestamp,
        "items": s.items or []
    }

@router.get("/feed", response_model=List[dict])
async def get_status_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(StatusStory).order_by(StatusStory.created_at.desc()))
    stories = result.scalars().all()
    return [format_status_dict(s, current_user.id) for s in stories]

@router.post("", response_model=dict)
async def create_status(
    req: StatusCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.utcnow()
    # Check if user already has an active status container
    result = await db.execute(select(StatusStory).where(StatusStory.user_id == current_user.id))
    existing = result.scalar_one_or_none()

    new_items = []
    for item in req.items:
        new_items.append({
            "id": f"item_{int(now.timestamp() * 1000)}",
            "type": item.type,
            "backgroundColor": item.backgroundColor,
            "text": item.text,
            "mediaUrl": item.mediaUrl,
            "caption": item.caption,
            "timestamp": "Just now",
            "views": 0,
            "viewers": []
        })

    if existing:
        current_items = list(existing.items or [])
        existing.items = new_items + current_items
        existing.timestamp = "Just now"
        await db.commit()
        await db.refresh(existing)
        return format_status_dict(existing, current_user.id)
    else:
        new_story = StatusStory(
            id=f"status_{current_user.id}",
            user_id=current_user.id,
            user_name=current_user.name,
            user_avatar=current_user.avatar,
            is_me=True,
            has_unseen=False,
            timestamp="Just now",
            items=new_items
        )
        db.add(new_story)
        await db.commit()
        await db.refresh(new_story)
        return format_status_dict(new_story, current_user.id)

@router.post("/{story_id}/views")
async def record_status_view(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(StatusStory).where(StatusStory.id == story_id))
    story = result.scalar_one_or_none()
    if story and story.items:
        items = list(story.items)
        for itm in items:
            viewers = itm.get("viewers", [])
            if current_user.name not in viewers:
                viewers.append(current_user.name)
                itm["viewers"] = viewers
                itm["views"] = itm.get("views", 0) + 1
        story.items = items
        await db.commit()
    return {"success": True}

@router.delete("/{story_id}")
async def delete_status(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(StatusStory).where(StatusStory.id == story_id))
    story = result.scalar_one_or_none()
    if story:
        await db.delete(story)
        await db.commit()
    return {"success": True}
