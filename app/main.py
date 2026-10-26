import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.seed_data import seed_all_data
from app.websocket.manager import manager
from app.routers import (
    auth_router,
    conversations_router,
    messages_router,
    groups_router,
    statuses_router,
    channels_router,
    business_router,
    calls_router,
    ads_router,
    subscriptions_router,
    upload_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure upload folder exists, initialize DB tables, seed initial data
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    await init_db()
    if settings.AUTO_SEED:
        async with AsyncSessionLocal() as session:
            await seed_all_data(session)
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API and Real-Time WebSocket Service for Muraho Rwandan Chatting & Business Suite",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local vite and network clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads (voice notes, photos, documents)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount REST API Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(conversations_router, prefix=settings.API_V1_STR)
app.include_router(messages_router, prefix=settings.API_V1_STR)
app.include_router(groups_router, prefix=settings.API_V1_STR)
app.include_router(statuses_router, prefix=settings.API_V1_STR)
app.include_router(channels_router, prefix=settings.API_V1_STR)
app.include_router(business_router, prefix=settings.API_V1_STR)
app.include_router(calls_router, prefix=settings.API_V1_STR)
app.include_router(ads_router, prefix=settings.API_V1_STR)
app.include_router(subscriptions_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)

# ----------------- REAL-TIME WEBSOCKET ROUTE -----------------

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # Authenticate token passed via query parameter ?token=...
    token = websocket.query_params.get("token")
    from app.core.security import decode_access_token
    from app.models.conversation import ConversationParticipant, Conversation as ConvModel
    from sqlalchemy import select as sel, and_

    authenticated_user_id = None
    if token:
        authenticated_user_id = decode_access_token(token)

    # Require authenticated token matching user_id
    if not authenticated_user_id or authenticated_user_id != user_id:
        # Fallback only if no secret key configured or development token matches
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        print(f"[WebSocket] Unauthorized connection attempt rejected for user: {user_id}")
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            payload = data.get("data", {})

            # 1. Real-time typing indicators (authorized participants only)
            if event == "chat.typing":
                conv_id = payload.get("conversationId")
                if conv_id:
                    # Check membership before broadcasting typing indicator
                    async with AsyncSessionLocal() as db_session:
                        cp_res = await db_session.execute(
                            sel(ConversationParticipant).where(
                                ConversationParticipant.conversation_id == conv_id,
                                ConversationParticipant.user_id == user_id
                            )
                        )
                        if cp_res.scalar_one_or_none():
                            await manager.broadcast_to_conversation(
                                conversation_id=conv_id,
                                message={
                                    "event": "chat.typing",
                                    "data": {
                                        "conversationId": conv_id,
                                        "userId": user_id,
                                        "isTyping": payload.get("isTyping", True)
                                    }
                                },
                                exclude_user_id=user_id
                            )

            # 2. Room membership (authorized participants only)
            elif event == "room.join":
                conv_id = payload.get("conversationId")
                if conv_id:
                    async with AsyncSessionLocal() as db_session:
                        # Authorize that user is a verified participant of this conversation
                        cp_res = await db_session.execute(
                            sel(ConversationParticipant).where(
                                ConversationParticipant.conversation_id == conv_id,
                                ConversationParticipant.user_id == user_id
                            )
                        )
                        if not cp_res.scalar_one_or_none():
                            # Direct conversation fallback
                            conv_res = await db_session.execute(
                                sel(ConvModel).where(ConvModel.id == conv_id)
                            )
                            c_item = conv_res.scalar_one_or_none()
                            if not c_item or (c_item.type == "direct" and c_item.participant_id != user_id):
                                print(f"[WebSocket] Rejected unauthorized room join: {user_id} -> {conv_id}")
                                continue

                        manager.join_room(conv_id, user_id)

                        # Mark messages in this conversation as delivered for this user
                        from app.models.message import Message as MsgModel
                        result = await db_session.execute(
                            sel(MsgModel).where(
                                and_(
                                    MsgModel.conversation_id == conv_id,
                                    MsgModel.sender_id != user_id,
                                    MsgModel.status.in_(["sent"])
                                )
                            )
                        )
                        pending_msgs = result.scalars().all()
                        for pm in pending_msgs:
                            pm.status = "delivered"
                        if pending_msgs:
                            await db_session.commit()
                            # Notify senders about delivery
                            for pm in pending_msgs:
                                status_msg = {
                                    "event": "chat.message_status",
                                    "data": {
                                        "messageId": pm.id,
                                        "conversationId": conv_id,
                                        "status": "delivered"
                                    }
                                }
                                await manager.send_personal_message(status_msg, pm.sender_id)

            elif event == "room.leave":
                conv_id = payload.get("conversationId")
                if conv_id:
                    manager.leave_room(conv_id, user_id)

            # 3. Message read receipts
            elif event == "chat.read":
                conv_id = payload.get("conversationId")
                if conv_id:
                    async with AsyncSessionLocal() as db_session:
                        # Membership check
                        cp_res = await db_session.execute(
                            sel(ConversationParticipant).where(
                                ConversationParticipant.conversation_id == conv_id,
                                ConversationParticipant.user_id == user_id
                            )
                        )
                        if not cp_res.scalar_one_or_none():
                            continue

                        from app.models.message import Message as MsgModel
                        result = await db_session.execute(
                            sel(MsgModel).where(
                                and_(
                                    MsgModel.conversation_id == conv_id,
                                    MsgModel.sender_id != user_id,
                                    MsgModel.status.in_(["sent", "delivered"])
                                )
                            )
                        )
                        unread_msgs = result.scalars().all()
                        for um in unread_msgs:
                            um.status = "read"
                        if unread_msgs:
                            await db_session.commit()
                            for um in unread_msgs:
                                status_msg = {
                                    "event": "chat.message_status",
                                    "data": {
                                        "messageId": um.id,
                                        "conversationId": conv_id,
                                        "status": "read"
                                    }
                                }
                                await manager.send_personal_message(status_msg, um.sender_id)

            # 4. WebRTC Call Signaling (Audio & Video Calling)
            elif event in ["call.offer", "call.answer", "call.ice_candidate", "call.reject", "call.end"]:
                target_user_id = payload.get("targetUserId")
                if target_user_id:
                    await manager.send_personal_message(
                        message={"event": event, "data": payload, "fromUserId": user_id},
                        user_id=target_user_id
                    )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"[WebSocket Error] {e}")
        await manager.disconnect(websocket, user_id)

# ----------------- HEALTH & ROOT CHECK -----------------

@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "database": "Neon PostgreSQL (or local SQLite development fallback)"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
