from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, JSON, Text
from app.database import Base

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="user_me", index=True)
    name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    location = Column(String, nullable=True)
    working_hours = Column(String, nullable=True)
    social_links = Column(JSON, default=dict)
    greeting_message = Column(Text, nullable=True)
    greeting_enabled = Column(Boolean, default=True)
    away_message = Column(Text, nullable=True)
    away_enabled = Column(Boolean, default=True)
    quick_replies = Column(JSON, default=list)
    ai_support = Column(JSON, default=lambda: {
        "enabled": True,
        "confidenceThreshold": 0.85,
        "autoHandoffToHuman": True,
        "faqs": []
    })
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    business_id = Column(String, default="biz_kigali_tech", index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="RWF")
    stock = Column(Integer, default=10)
    status = Column(String, default="in_stock") # 'in_stock', 'out_of_stock'
    image = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    sales_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerTicket(Base):
    __tablename__ = "customer_tickets"

    id = Column(String, primary_key=True, index=True)
    business_id = Column(String, default="biz_kigali_tech", index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_avatar = Column(String, nullable=True)
    issue_summary = Column(Text, nullable=False)
    last_message = Column(Text, nullable=True)
    timestamp = Column(String, default="Just now")
    status = Column(String, default="Open") # 'Open', 'Pending', 'Resolved'
    priority = Column(String, default="Normal") # 'High', 'Normal', 'Low'
    channel = Column(String, default="Chat")
    notes = Column(JSON, default=list) # List of note strings
    unread = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessAnalytics(Base):
    __tablename__ = "business_analytics"

    id = Column(String, primary_key=True, index=True)
    business_id = Column(String, default="biz_kigali_tech", index=True)
    total_messages = Column(Integer, default=1420)
    response_rate = Column(String, default="98.4%")
    avg_response_time = Column(String, default="1.8m")
    active_customers = Column(Integer, default=380)
    revenue_rwf = Column(Integer, default=4850000)
    daily_conversations = Column(JSON, default=list)
    channel_breakdown = Column(JSON, default=list)
    satisfaction_rate = Column(String, default="4.9/5")
    updated_at = Column(DateTime, default=datetime.utcnow)
