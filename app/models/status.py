from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from app.database import Base

class StatusStory(Base):
    __tablename__ = "statuses"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    user_name = Column(String, nullable=False)
    user_avatar = Column(String, nullable=True)
    is_me = Column(Boolean, default=False)
    has_unseen = Column(Boolean, default=True)
    timestamp = Column(String, default="Just now")
    items = Column(JSON, default=list) # List of status items
    created_at = Column(DateTime, default=datetime.utcnow)
