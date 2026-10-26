from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from app.database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tagline = Column(String, nullable=True)
    price_monthly = Column(Integer, default=0)
    price_yearly = Column(Integer, default=0)
    badge = Column(String, nullable=True)
    highlight = Column(Boolean, default=False)
    features = Column(JSON, default=list)
    button_text = Column(String, default="Select Plan")

class BillingInvoice(Base):
    __tablename__ = "billing_invoices"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="user_me", index=True)
    invoice_number = Column(String, unique=True, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    status = Column(String, default="Paid")
    payment_method = Column(String, default="MTN MoMo (*182#)")
    created_at = Column(DateTime, default=datetime.utcnow)
