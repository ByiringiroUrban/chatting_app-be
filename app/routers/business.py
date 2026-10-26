from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.business import BusinessProfile, Product, CustomerTicket, BusinessAnalytics
from app.models.user import User
from app.schemas.all_schemas import (
    ProductCreateRequest, ProductUpdateRequest, ProductResponse,
    CustomerTicketUpdate, AiSupportTestRequest, FaqCreateRequest
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/business", tags=["Business Suite"])

def format_product_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "currency": p.currency or "RWF",
        "stock": p.stock,
        "status": p.status,
        "image": p.image,
        "description": p.description,
        "salesCount": p.sales_count
    }

def format_ticket_dict(t: CustomerTicket) -> dict:
    return {
        "id": t.id,
        "customerName": t.customer_name,
        "customerPhone": t.customer_phone,
        "customerAvatar": t.customer_avatar,
        "issueSummary": t.issue_summary,
        "lastMessage": t.last_message,
        "timestamp": t.timestamp,
        "status": t.status,
        "priority": t.priority,
        "channel": t.channel,
        "notes": t.notes or [],
        "unread": t.unread
    }

# ----------------- BUSINESS PROFILE -----------------

@router.get("/profile")
async def get_business_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not initialized")
    return {
        "id": profile.id,
        "name": profile.name,
        "logo": profile.logo,
        "category": profile.category,
        "description": profile.description,
        "email": profile.email,
        "phone": profile.phone,
        "website": profile.website,
        "location": profile.location,
        "workingHours": profile.working_hours,
        "socialLinks": profile.social_links or {},
        "greetingMessage": profile.greeting_message,
        "greetingEnabled": profile.greeting_enabled,
        "awayMessage": profile.away_message,
        "awayEnabled": profile.away_enabled,
        "quickReplies": profile.quick_replies or [],
        "aiSupport": profile.ai_support or {}
    }

@router.patch("/profile")
async def update_business_profile(updates: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    for k, v in updates.items():
        if hasattr(profile, k):
            setattr(profile, k, v)
        elif k == "aiSupport":
            profile.ai_support = v
        elif k == "quickReplies":
            profile.quick_replies = v
        elif k == "socialLinks":
            profile.social_links = v

    await db.commit()
    await db.refresh(profile)
    return {"success": True, "message": "Business profile updated"}

@router.post("/faqs")
async def add_faq(req: FaqCreateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    ai_support = dict(profile.ai_support or {})
    faqs = list(ai_support.get("faqs", []))
    new_faq = {
        "id": f"faq_{int(datetime.utcnow().timestamp() * 1000)}",
        "question": req.question,
        "answer": req.answer
    }
    faqs.append(new_faq)
    ai_support["faqs"] = faqs
    profile.ai_support = ai_support
    await db.commit()
    return new_faq

@router.delete("/faqs/{faq_id}")
async def delete_faq(faq_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    ai_support = dict(profile.ai_support or {})
    faqs = [f for f in ai_support.get("faqs", []) if f.get("id") != faq_id]
    ai_support["faqs"] = faqs
    profile.ai_support = ai_support
    await db.commit()
    return {"success": True}

# ----------------- PRODUCT CATALOG -----------------

@router.get("/catalog", response_model=List[dict])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    return [format_product_dict(p) for p in products]

@router.post("/catalog", response_model=dict)
async def create_product(req: ProductCreateRequest, db: AsyncSession = Depends(get_db)):
    new_prod_id = f"prod_{int(datetime.utcnow().timestamp() * 1000)}"
    new_product = Product(
        id=new_prod_id,
        name=req.name,
        category=req.category,
        price=req.price,
        currency="RWF",
        stock=req.stock,
        status="in_stock" if req.stock > 0 else "out_of_stock",
        image=req.image or "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
        description=req.description or "",
        sales_count=0
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return format_product_dict(new_product)

@router.patch("/catalog/{product_id}", response_model=dict)
async def update_product(product_id: str, req: ProductUpdateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    if req.name is not None:
        prod.name = req.name
    if req.category is not None:
        prod.category = req.category
    if req.price is not None:
        prod.price = req.price
    if req.stock is not None:
        prod.stock = req.stock
        prod.status = "in_stock" if req.stock > 0 else "out_of_stock"
    if req.status is not None:
        prod.status = req.status
    if req.image is not None:
        prod.image = req.image
    if req.description is not None:
        prod.description = req.description

    await db.commit()
    await db.refresh(prod)
    return format_product_dict(prod)

@router.delete("/catalog/{product_id}")
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(prod)
    await db.commit()
    return {"success": True, "productId": product_id}

# ----------------- CUSTOMER INBOX -----------------

@router.get("/inbox", response_model=List[dict])
async def list_customer_tickets(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(CustomerTicket)
    if status_filter and status_filter.lower() != "all":
        query = query.where(CustomerTicket.status == status_filter)
    result = await db.execute(query.order_by(CustomerTicket.created_at.desc()))
    tickets = result.scalars().all()
    return [format_ticket_dict(t) for t in tickets]

@router.patch("/inbox/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    req: CustomerTicketUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CustomerTicket).where(CustomerTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if req.status is not None:
        ticket.status = req.status
    if req.priority is not None:
        ticket.priority = req.priority
    if req.note:
        notes = list(ticket.notes or [])
        notes.append(f"{datetime.utcnow().strftime('%b %d, %H:%M')}: {req.note}")
        ticket.notes = notes

    ticket.unread = False
    await db.commit()
    await db.refresh(ticket)
    return format_ticket_dict(ticket)

# ----------------- ANALYTICS & AI SUPPORT -----------------

@router.get("/analytics")
async def get_business_analytics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessAnalytics).limit(1))
    analytics = result.scalar_one_or_none()
    if not analytics:
        # Fallback default metrics
        return {
            "totalMessages": 1420,
            "responseRate": "98.4%",
            "avgResponseTime": "1.8m",
            "activeCustomers": 380,
            "revenueRwf": 4850000,
            "dailyConversations": [
                { "day": "Mon", "count": 180 },
                { "day": "Tue", "count": 220 },
                { "day": "Wed", "count": 290 },
                { "day": "Thu", "count": 240 },
                { "day": "Fri", "count": 310 },
                { "day": "Sat", "count": 190 },
                { "day": "Sun", "count": 140 }
            ],
            "channelBreakdown": [
                { "name": "Direct Chat", "value": 65 },
                { "name": "Catalog Share", "value": 20 },
                { "name": "MoMo Pay Link", "value": 15 }
            ],
            "customerSatisfaction": "4.9/5"
        }
    return {
        "totalMessages": analytics.total_messages,
        "responseRate": analytics.response_rate,
        "avgResponseTime": analytics.avg_response_time,
        "activeCustomers": analytics.active_customers,
        "revenueRwf": analytics.revenue_rwf,
        "dailyConversations": analytics.daily_conversations or [],
        "channelBreakdown": analytics.channel_breakdown or [],
        "customerSatisfaction": analytics.satisfaction_rate
    }

@router.post("/ai-support/test")
async def test_ai_support(req: AiSupportTestRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessProfile).limit(1))
    profile = result.scalar_one_or_none()
    
    question_lower = req.question.lower()
    faqs = (profile.ai_support or {}).get("faqs", []) if profile else []
    
    best_match = None
    best_score = 0
    
    # Simple semantic keyword match
    for f in faqs:
        f_q = f.get("question", "").lower()
        words = [w for w in f_q.split() if len(w) > 3]
        matches = sum(1 for w in words if w in question_lower)
        score = matches / max(1, len(words))
        if score > best_score:
            best_score = score
            best_match = f
            
    if best_match and best_score >= 0.25:
        return {
            "answer": best_match.get("answer"),
            "confidence": round(min(0.98, 0.70 + best_score * 0.3), 2),
            "matchedFaq": best_match.get("question"),
            "status": "answered"
        }
    else:
        return {
            "answer": "Muraho! I have forwarded your question to our human customer support specialist in Kigali. A team member will reply shortly.",
            "confidence": 0.42,
            "matchedFaq": None,
            "status": "escalated_to_human"
        }
