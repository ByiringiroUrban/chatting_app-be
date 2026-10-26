from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database import Base

class CallLog(Base):
    __tablename__ = "call_history"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="user_me", index=True)
    contact_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    type = Column(String, default="voice") # 'voice', 'video'
    direction = Column(String, default="outgoing") # 'incoming', 'outgoing', 'missed'
    status = Column(String, default="completed") # 'completed', 'missed', 'rejected'
    timestamp = Column(String, default="Just now")
    duration = Column(String, default="0s")
    created_at = Column(DateTime, default=datetime.utcnow)
