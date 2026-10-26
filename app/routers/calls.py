from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.call import CallLog
from app.models.user import User
from app.schemas.all_schemas import CallLogCreateRequest, CallLogResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/calls", tags=["Audio & Video Calls"])

def format_call_dict(c: CallLog) -> dict:
    return {
        "id": c.id,
        "contactId": c.contact_id,
        "name": c.name,
        "avatar": c.avatar,
        "type": c.type,
        "direction": c.direction,
        "status": c.status,
        "timestamp": c.timestamp,
        "duration": c.duration
    }

@router.get("/history", response_model=List[dict])
async def get_call_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CallLog).order_by(desc(CallLog.created_at)))
    calls = result.scalars().all()
    return [format_call_dict(c) for c in calls]

@router.post("/log", response_model=dict)
async def log_call(
    req: CallLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    call_id = f"call_{int(datetime.utcnow().timestamp() * 1000)}"
    time_str = datetime.utcnow().strftime("Today, %I:%M %p")
    new_call = CallLog(
        id=call_id,
        user_id=current_user.id,
        contact_id=req.contactId,
        name=req.name,
        avatar=req.avatar,
        type=req.type,
        direction=req.direction,
        status=req.status,
        timestamp=time_str,
        duration=req.duration or "0s"
    )
    db.add(new_call)
    await db.commit()
    await db.refresh(new_call)
    return format_call_dict(new_call)
