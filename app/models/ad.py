from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from app.database import Base

class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="user_me", index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    audience = Column(String, nullable=True)
    budget_rwf = Column(Float, default=100000)
    spent_rwf = Column(Float, default=0)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    status = Column(String, default="Active") # 'Active', 'Paused', 'Completed'
    creative_url = Column(String, nullable=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(String, default="0.00%")
    conversions = Column(Integer, default=0)
    cpc_rwf = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
