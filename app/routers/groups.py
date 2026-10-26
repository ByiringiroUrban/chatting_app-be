from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.group import Group
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.all_schemas import GroupCreateRequest, GroupResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/groups", tags=["Groups"])

def format_group_dict(g: Group) -> dict:
    return {
        "id": g.id,
        "name": g.name,
        "avatar": g.avatar,
        "description": g.description,
        "createdAt": g.created_at,
        "members": g.members or [],
        "settings": g.settings or {}
    }

from app.models.conversation import Conversation, ConversationParticipant

@router.get("", response_model=List[dict])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns only groups where current_user is a participant or creator.
    """
    result = await db.execute(select(Group))
    groups = result.scalars().all()
    # Filter groups where current_user is in members list
    user_groups = [
        format_group_dict(g) for g in groups
        if any(m.get("id") == current_user.id for m in (g.members or []))
    ]
    return user_groups

@router.post("", response_model=dict)
async def create_group(
    req: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    group_id = f"group_{int(datetime.utcnow().timestamp())}"
    
    # Resolve member list
    members = [
        {
            "id": current_user.id,
            "name": current_user.name,
            "role": "admin",
            "avatar": current_user.avatar
        }
    ]
    
    member_user_ids = [current_user.id]
    for uid in req.memberIds:
        if uid != current_user.id:
            user_res = await db.execute(select(User).where(User.id == uid))
            u = user_res.scalar_one_or_none()
            if u:
                members.append({
                    "id": u.id,
                    "name": u.name,
                    "role": "member",
                    "avatar": u.avatar
                })
                member_user_ids.append(u.id)

    new_group = Group(
        id=group_id,
        name=req.name,
        avatar=req.avatar or "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=300&q=80",
        description=req.description or "Community group on Muraho Rwanda",
        created_at=datetime.utcnow().strftime("%Y-%m-%d"),
        members=members,
        settings={"onlyAdminsCanPost": False, "approveNewMembers": True, "allowMediaSharing": True}
    )
    db.add(new_group)
    
    # Also create matching Conversation so it shows in chats
    conv_id = f"conv_{group_id}"
    new_conv = Conversation(
        id=conv_id,
        type="group",
        group_id=group_id,
        name=req.name,
        avatar=new_group.avatar,
        member_count=len(members),
        tags=["Community"]
    )
    db.add(new_conv)

    # Insert ConversationParticipant for each group member
    for mid in member_user_ids:
        cp = ConversationParticipant(
            id=f"cp_{conv_id}_{mid}",
            conversation_id=conv_id,
            user_id=mid,
            role="admin" if mid == current_user.id else "member"
        )
        db.add(cp)

    await db.commit()
    await db.refresh(new_group)
    return format_group_dict(new_group)

@router.get("/{group_id}", response_model=dict)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Authorize membership
    if not any(m.get("id") == current_user.id for m in (group.members or [])):
        raise HTTPException(status_code=403, detail="Access denied. You are not a member of this group.")

    return format_group_dict(group)

@router.post("/{group_id}/members")
async def add_member(
    group_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Must be existing member (or admin) to add members
    if not any(m.get("id") == current_user.id for m in (group.members or [])):
        raise HTTPException(status_code=403, detail="Access denied. Only group members can invite others.")

    user_res = await db.execute(select(User).where(User.id == user_id))
    u = user_res.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    members = list(group.members or [])
    if not any(m["id"] == u.id for m in members):
        members.append({
            "id": u.id,
            "name": u.name,
            "role": "member",
            "avatar": u.avatar
        })
        group.members = members

        # Also add ConversationParticipant
        conv_id = f"conv_{group_id}"
        cp_check = await db.execute(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conv_id,
                ConversationParticipant.user_id == u.id
            )
        )
        if not cp_check.scalar_one_or_none():
            cp = ConversationParticipant(
                id=f"cp_{conv_id}_{u.id}",
                conversation_id=conv_id,
                user_id=u.id,
                role="member"
            )
            db.add(cp)

        await db.commit()

    return {"success": True, "members": group.members}

@router.delete("/{group_id}/members/{user_id}")
async def remove_member(
    group_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Only self-removal (leave group) or admin can remove members
    is_self = (user_id == current_user.id)
    is_admin = any(m.get("id") == current_user.id and m.get("role") == "admin" for m in (group.members or []))
    if not (is_self or is_admin):
        raise HTTPException(status_code=403, detail="Forbidden. Only group admins or the member themselves can perform this action.")

    members = [m for m in (group.members or []) if m.get("id") != user_id]
    group.members = members

    # Remove ConversationParticipant
    conv_id = f"conv_{group_id}"
    cp_res = await db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conv_id,
            ConversationParticipant.user_id == user_id
        )
    )
    cp = cp_res.scalar_one_or_none()
    if cp:
        await db.delete(cp)

    await db.commit()
    return {"success": True, "members": group.members}
