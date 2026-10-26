from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Text, ForeignKey
from app.database import Base

class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    handle = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String, nullable=True)
    category = Column(String, default="General")
    description = Column(Text, nullable=True)
    subscribers = Column(Integer, default=0)
    is_subscribed = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    posts = Column(JSON, default=list) # List of post items
    created_at = Column(DateTime, default=datetime.utcnow)

class ChannelSubscription(Base):
    __tablename__ = "channel_subscriptions"

    id = Column(String, primary_key=True, index=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
