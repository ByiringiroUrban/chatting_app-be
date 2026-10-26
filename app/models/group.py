from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey
from app.database import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    members = Column(JSON, default=list) # List of member objects
    settings = Column(JSON, default=lambda: {
        "onlyAdminsCanPost": False,
        "approveNewMembers": True,
        "allowMediaSharing": True
    })

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, default="member") # 'admin', 'member'
    joined_at = Column(DateTime, default=datetime.utcnow)
