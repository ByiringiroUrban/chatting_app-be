from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, default="direct") # 'direct' or 'group'
    participant_id = Column(String, nullable=True) # For direct chats (the other user)
    group_id = Column(String, nullable=True) # For group chats
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    member_count = Column(Integer, default=2)
    is_pinned = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    unread_count = Column(Integer, default=0)
    draft = Column(String, default="")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, default="member") # 'admin', 'member'
    is_pinned = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    unread_count = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)
