import json
from typing import Dict, Set, Any
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps user_id -> Set of active WebSocket connections (support multiple devices/tabs)
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Maps conversation_id -> Set of user_ids currently viewing the chat
        self.conversation_rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Broadcast user online presence
        await self.broadcast_presence(user_id, status="online")
        print(f"[WebSocket] User connected: {user_id} (active tabs: {len(self.active_connections[user_id])})")

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Broadcast user offline presence
                await self.broadcast_presence(user_id, status="offline")
        
        # Remove from any conversation rooms
        for room_users in self.conversation_rooms.values():
            room_users.discard(user_id)
            
        print(f"[WebSocket] User disconnected: {user_id}")

    def join_room(self, conversation_id: str, user_id: str):
        if conversation_id not in self.conversation_rooms:
            self.conversation_rooms[conversation_id] = set()
        self.conversation_rooms[conversation_id].add(user_id)

    def leave_room(self, conversation_id: str, user_id: str):
        if conversation_id in self.conversation_rooms:
            self.conversation_rooms[conversation_id].discard(user_id)

    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Sends a JSON message to all open tabs for a specific user"""
        if user_id in self.active_connections:
            dead_connections = set()
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.add(ws)
            self.active_connections[user_id] -= dead_connections

    async def broadcast_to_users(self, message: Dict[str, Any], user_ids: list[str]):
        """Sends a JSON message to a list of specific user IDs"""
        for uid in user_ids:
            await self.send_personal_message(message, uid)

    async def broadcast_to_conversation(self, conversation_id: str, message: Dict[str, Any], exclude_user_id: str = None):
        """Broadcasts a message to all users in a conversation"""
        target_users = self.conversation_rooms.get(conversation_id, set())
        for uid in target_users:
            if uid != exclude_user_id:
                await self.send_personal_message(message, uid)

    async def broadcast_presence(self, user_id: str, status: str):
        """Broadcasts online/offline status change to all connected clients"""
        presence_msg = {
            "event": "user.presence",
            "data": {
                "userId": user_id,
                "status": status,
                "lastSeen": "Just now" if status == "online" else "Recently"
            }
        }
        for uid, connections in list(self.active_connections.items()):
            if uid != user_id:
                for ws in list(connections):
                    try:
                        await ws.send_json(presence_msg)
                    except Exception:
                        pass

manager = ConnectionManager()
