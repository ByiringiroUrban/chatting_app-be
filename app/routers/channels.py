from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.channel import Channel, ChannelSubscription
from app.models.user import User
from app.schemas.all_schemas import ChannelPostCreateRequest, ReactionRequest
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/channels", tags=["Channels"])

def format_channel_dict(c: Channel) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "handle": c.handle,
        "avatar": c.avatar,
        "category": c.category,
        "description": c.description,
        "subscribers": c.subscribers,
        "isSubscribed": c.is_subscribed,
        "isVerified": c.is_verified,
        "isPremium": c.is_premium,
        "posts": c.posts or []
    }

@router.get("", response_model=List[dict])
async def list_channels(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Channel)
    if category and category.lower() != "all":
        query = query.where(Channel.category == category)
    result = await db.execute(query)
    channels = result.scalars().all()
    return [format_channel_dict(c) for c in channels]

@router.get("/{channel_id}", response_model=dict)
async def get_channel(channel_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    return format_channel_dict(ch)

@router.post("/{channel_id}/subscribe")
async def toggle_subscribe_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    ch.is_subscribed = not ch.is_subscribed
    ch.subscribers = max(0, ch.subscribers + (1 if ch.is_subscribed else -1))
    await db.commit()
    return {"id": ch.id, "isSubscribed": ch.is_subscribed, "subscribers": ch.subscribers}

@router.post("/{channel_id}/posts")
async def create_channel_post(
    channel_id: str,
    req: ChannelPostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    now = datetime.utcnow()
    new_post = {
        "id": f"post_{int(now.timestamp() * 1000)}",
        "title": req.title,
        "content": req.content,
        "mediaUrl": req.mediaUrl,
        "timestamp": "Just now",
        "views": "1",
        "reactions": []
    }
    posts = list(ch.posts or [])
    ch.posts = [new_post] + posts
    await db.commit()
    return new_post

@router.post("/{channel_id}/posts/{post_id}/react")
async def react_channel_post(
    channel_id: str,
    post_id: str,
    req: ReactionRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    posts = list(ch.posts or [])
    for p in posts:
        if p.get("id") == post_id:
            reactions = list(p.get("reactions") or [])
            found = False
            for r in reactions:
                if r.get("emoji") == req.emoji:
                    r["count"] = r.get("count", 0) + 1
                    found = True
                    break
            if not found:
                reactions.append({"emoji": req.emoji, "count": 1})
            p["reactions"] = reactions
            break
            
    ch.posts = posts
    await db.commit()
    return {"success": True}
