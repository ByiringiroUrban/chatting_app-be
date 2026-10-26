from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_
from app.database import get_db
from app.models.conversation import Conversation, ConversationParticipant
from app.models.message import Message
from app.models.user import User
from app.schemas.all_schemas import (
    ConversationResponse, ConversationCreateRequest,
    MessageResponse, MessageSendRequest
)
from app.core.dependencies import get_current_user
from app.websocket.manager import manager

router = APIRouter(prefix="/conversations", tags=["Conversations"])

def format_message_dict(m: Message) -> dict:
    return {
        "id": m.id,
        "conversationId": m.conversation_id,
        "senderId": m.sender_id,
        "senderName": m.sender_name,
        "senderAvatar": m.sender_avatar,
        "text": m.text,
        "timestamp": m.timestamp,
        "date": m.date or "Today",
        "status": m.status,
        "type": m.type,
        "mediaUrl": m.media_url,
        "fileName": m.file_name,
        "fileSize": m.file_size,
        "duration": m.duration,
        "caption": m.caption,
        "isPinned": m.is_pinned,
        "isEdited": m.is_edited,
        "isForwarded": m.is_forwarded,
        "replyTo": m.reply_to,
        "reactions": m.reactions or []
    }

def format_conversation_dict(
    c: Conversation,
    current_user_id: str,
    participant_user: Optional[User] = None,
    cp: Optional[ConversationParticipant] = None,
    last_msg: Optional[Message] = None
) -> dict:
    last_msg_dict = format_message_dict(last_msg) if last_msg else None

    # For direct conversations, dynamic display name and avatar must reflect the *other* party
    if c.type == "direct":
        if participant_user:
            display_name = participant_user.name
            display_avatar = participant_user.avatar
            participant_id = participant_user.id
            status_val = participant_user.status
        else:
            display_name = c.name
            display_avatar = c.avatar
            participant_id = c.participant_id
            status_val = "offline"
    else:
        display_name = c.name
        display_avatar = c.avatar
        participant_id = None
        status_val = None

    is_pinned = cp.is_pinned if cp else c.is_pinned
    is_muted = cp.is_muted if cp else c.is_muted
    unread_count = cp.unread_count if (cp and cp.unread_count is not None) else (c.unread_count or 0)

    return {
        "id": c.id,
        "type": c.type,
        "participantId": participant_id,
        "groupId": c.group_id,
        "name": display_name,
        "avatar": display_avatar,
        "memberCount": c.member_count,
        "isPinned": bool(is_pinned),
        "isMuted": bool(is_muted),
        "unreadCount": unread_count,
        "status": status_val,
        "isTyping": False,
        "typingUser": None,
        "lastMessage": last_msg_dict,
        "draft": c.draft or "",
        "tags": c.tags or []
    }

async def verify_conversation_participant(
    conversation_id: str,
    user_id: str,
    db: AsyncSession
) -> tuple[Conversation, Optional[ConversationParticipant]]:
    """
    Checks that the user is an authorized participant of the conversation.
    Raises 404 or 403 if unauthorized.
    """
    conv_result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = conv_result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    cp_result = await db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id
        )
    )
    cp = cp_result.scalar_one_or_none()

    if not cp:
        # Fallback for direct conversations if participant_id matches
        if conv.type == "direct" and (conv.participant_id == user_id):
            return conv, None
        raise HTTPException(status_code=403, detail="Access denied. You are not a participant in this conversation.")

    return conv, cp

@router.get("", response_model=List[dict])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns ONLY conversations that the currently logged-in user belongs to.
    """
    # 1. Fetch participant records for current user
    cp_query = select(ConversationParticipant).where(ConversationParticipant.user_id == current_user.id)
    cp_result = await db.execute(cp_query)
    cp_records = {cp.conversation_id: cp for cp in cp_result.scalars().all()}

    if not cp_records:
        return []

    # 2. Fetch the corresponding conversation entities
    conv_query = select(Conversation).where(Conversation.id.in_(list(cp_records.keys()))).order_by(desc(Conversation.updated_at))
    conv_result = await db.execute(conv_query)
    conversations = conv_result.scalars().all()

    # Preload other participants for direct chats
    other_user_ids = set()
    direct_conv_map = {}
    for c in conversations:
        if c.type == "direct":
            # Find the other participant in this conversation
            parts_res = await db.execute(
                select(ConversationParticipant.user_id)
                .where(
                    ConversationParticipant.conversation_id == c.id,
                    ConversationParticipant.user_id != current_user.id
                )
            )
            other_uid = parts_res.scalar_one_or_none() or c.participant_id
            if other_uid:
                other_user_ids.add(other_uid)
                direct_conv_map[c.id] = other_uid

    user_map = {}
    if other_user_ids:
        users_res = await db.execute(select(User).where(User.id.in_(list(other_user_ids))))
        user_map = {u.id: u for u in users_res.scalars().all()}

    response = []
    for c in conversations:
        cp = cp_records.get(c.id)
        other_user = user_map.get(direct_conv_map.get(c.id)) if c.type == "direct" else None

        # Get latest message
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == c.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()

        response.append(format_conversation_dict(
            c,
            current_user_id=current_user.id,
            participant_user=other_user,
            cp=cp,
            last_msg=last_msg
        ))

    # Sort pinned first, then by updated_at
    response.sort(key=lambda x: (1 if x["isPinned"] else 0, x["lastMessage"]["timestamp"] if x["lastMessage"] else ""), reverse=True)
    return response

@router.post("", response_model=dict)
async def create_conversation(
    req: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new conversation with current_user as a verified participant.
    If a direct conversation between these two users already exists, returns it.
    """
    target_user_id = req.participantId

    if req.type == "direct" and target_user_id:
        if target_user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot start a private conversation with yourself.")

        # Check if recipient user exists
        target_res = await db.execute(select(User).where(User.id == target_user_id))
        target_user = target_res.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found.")

        # Check if direct conversation already exists between current_user and target_user
        # Lookup all direct convs for current_user, then check if target is in it
        my_conv_ids_res = await db.execute(
            select(ConversationParticipant.conversation_id).where(ConversationParticipant.user_id == current_user.id)
        )
        my_conv_ids = [r[0] for r in my_conv_ids_res.all()]

        if my_conv_ids:
            existing_shared = await db.execute(
                select(ConversationParticipant.conversation_id)
                .join(Conversation, Conversation.id == ConversationParticipant.conversation_id)
                .where(
                    ConversationParticipant.conversation_id.in_(my_conv_ids),
                    ConversationParticipant.user_id == target_user_id,
                    Conversation.type == "direct"
                )
            )
            existing_conv_id = existing_shared.scalar_one_or_none()
            if existing_conv_id:
                conv_res = await db.execute(select(Conversation).where(Conversation.id == existing_conv_id))
                conv = conv_res.scalar_one_or_none()
                return format_conversation_dict(conv, current_user.id, participant_user=target_user)

    conv_id = f"conv_{int(datetime.utcnow().timestamp() * 1000)}"
    new_conv = Conversation(
        id=conv_id,
        type=req.type,
        participant_id=target_user_id if req.type == "direct" else None,
        name=req.name,
        avatar=req.avatar,
        tags=req.tags or []
    )
    db.add(new_conv)

    # Add creator as participant
    cp_me = ConversationParticipant(
        id=f"cp_{conv_id}_{current_user.id}",
        conversation_id=conv_id,
        user_id=current_user.id,
        role="admin" if req.type == "group" else "member"
    )
    db.add(cp_me)

    target_user = None
    if req.type == "direct" and target_user_id:
        target_res = await db.execute(select(User).where(User.id == target_user_id))
        target_user = target_res.scalar_one_or_none()
        cp_other = ConversationParticipant(
            id=f"cp_{conv_id}_{target_user_id}",
            conversation_id=conv_id,
            user_id=target_user_id,
            role="member"
        )
        db.add(cp_other)

    await db.commit()
    await db.refresh(new_conv)
    return format_conversation_dict(new_conv, current_user.id, participant_user=target_user)

@router.get("/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv, cp = await verify_conversation_participant(conversation_id, current_user.id, db)
    
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    last_msg = msg_result.scalar_one_or_none()

    # Preload other participant if direct
    other_user = None
    if conv.type == "direct":
        part_res = await db.execute(
            select(ConversationParticipant.user_id).where(
                ConversationParticipant.conversation_id == conv.id,
                ConversationParticipant.user_id != current_user.id
            )
        )
        other_uid = part_res.scalar_one_or_none() or conv.participant_id
        if other_uid:
            u_res = await db.execute(select(User).where(User.id == other_uid))
            other_user = u_res.scalar_one_or_none()

    return format_conversation_dict(conv, current_user.id, participant_user=other_user, cp=cp, last_msg=last_msg)

@router.patch("/{conversation_id}/pin")
async def toggle_pin_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv, cp = await verify_conversation_participant(conversation_id, current_user.id, db)
    if cp:
        cp.is_pinned = not cp.is_pinned
        await db.commit()
        return {"id": conv.id, "isPinned": cp.is_pinned}
    else:
        conv.is_pinned = not conv.is_pinned
        await db.commit()
        return {"id": conv.id, "isPinned": conv.is_pinned}

@router.patch("/{conversation_id}/mute")
async def toggle_mute_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv, cp = await verify_conversation_participant(conversation_id, current_user.id, db)
    if cp:
        cp.is_muted = not cp.is_muted
        await db.commit()
        return {"id": conv.id, "isMuted": cp.is_muted}
    else:
        conv.is_muted = not conv.is_muted
        await db.commit()
        return {"id": conv.id, "isMuted": conv.is_muted}

@router.patch("/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv, cp = await verify_conversation_participant(conversation_id, current_user.id, db)
    if cp:
        cp.unread_count = 0
    conv.unread_count = 0
    await db.commit()
    return {"success": True}

@router.get("/{conversation_id}/messages", response_model=List[dict])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Strict membership check
    await verify_conversation_participant(conversation_id, current_user.id, db)

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [format_message_dict(m) for m in messages]

@router.post("/{conversation_id}/messages", response_model=dict)
async def send_message(
    conversation_id: str,
    req: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Strict membership check: Only participants can send messages
    conv, _ = await verify_conversation_participant(conversation_id, current_user.id, db)

    # Enforce existing blocking rules for direct conversations
    if conv.type == "direct":
        # Check if recipient blocked sender or sender blocked recipient
        part_result = await db.execute(
            select(ConversationParticipant.user_id)
            .where(ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id != current_user.id)
        )
        recipient_id = part_result.scalar_one_or_none() or conv.participant_id
        if recipient_id:
            # Check if contact is blocked
            from app.models.user import Contact
            block_check = await db.execute(
                select(Contact).where(
                    or_(
                        and_(Contact.user_id == recipient_id, Contact.contact_id == current_user.id, Contact.is_blocked == True),
                        and_(Contact.user_id == current_user.id, Contact.contact_id == recipient_id, Contact.is_blocked == True)
                    )
                )
            )
            if block_check.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Cannot send message. This contact is blocked.")

    now = datetime.utcnow()
    time_str = now.strftime("%I:%M %p")
    msg_id = f"msg_{int(now.timestamp() * 1000)}"

    new_msg = Message(
        id=msg_id,
        conversation_id=conversation_id,
        sender_id=current_user.id,
        sender_name=current_user.name,
        sender_avatar=current_user.avatar,
        text=req.text or req.caption or (f"Voice note ({req.duration or '0:15'})" if req.type == "audio" else req.fileName or ""),
        timestamp=time_str,
        date="Today",
        status="sent",
        type=req.type,
        media_url=req.mediaUrl,
        file_name=req.fileName,
        file_size=req.fileSize,
        duration=req.duration,
        caption=req.caption,
        reply_to=req.replyTo.dict() if req.replyTo else None,
        reactions=[]
    )
    db.add(new_msg)
    conv.updated_at = now
    await db.commit()
    await db.refresh(new_msg)

    msg_dict = format_message_dict(new_msg)

    # Fetch all participants of this conversation to ensure targeted notification
    part_result = await db.execute(
        select(ConversationParticipant.user_id)
        .where(ConversationParticipant.conversation_id == conversation_id)
    )
    participant_ids = [r[0] for r in part_result.all()]
    if not participant_ids and conv.type == "direct":
        participant_ids = [current_user.id, conv.participant_id]

    # Real-time WebSocket delivery ONLY to verified participants
    room_users = manager.conversation_rooms.get(conversation_id, set())
    for pid in participant_ids:
        if pid == current_user.id:
            continue
        # If user is in the room, broadcast room message
        # If user is connected online but in another room, send targeted personal event
        await manager.send_personal_message(
            message={"event": "chat.message", "data": msg_dict},
            user_id=pid
        )

    # Increment unread count for other participants
    await db.execute(
        select(ConversationParticipant)
        .where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id != current_user.id
        )
    )
    other_cps = await db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id != current_user.id
        )
    )
    for ocp in other_cps.scalars().all():
        ocp.unread_count = (ocp.unread_count or 0) + 1

    conv.unread_count = (conv.unread_count or 0) + 1
    await db.commit()

    return msg_dict
