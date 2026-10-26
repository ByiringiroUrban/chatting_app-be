from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String, nullable=False, index=True)
    sender_name = Column(String, nullable=True)
    sender_avatar = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    timestamp = Column(String, nullable=True)
    date = Column(String, default="Today")
    status = Column(String, default="sent") # 'sent', 'delivered', 'read'
    type = Column(String, default="text") # 'text', 'image', 'audio', 'document'
    media_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    is_forwarded = Column(Boolean, default=False)
    reply_to = Column(JSON, nullable=True) # { "id": "...", "senderName": "...", "text": "..." }
    reactions = Column(JSON, default=list) # [ { "emoji": "🔥", "count": 1, "users": ["user_me"] } ]
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    conversation = relationship("Conversation", back_populates="messages")
