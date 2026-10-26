from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.subscription import SubscriptionPlan, BillingInvoice
from app.models.user import User
from app.schemas.all_schemas import CheckoutRequest
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions & Monetization"])

def format_plan_dict(p: SubscriptionPlan) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "tagline": p.tagline,
        "priceMonthly": p.price_monthly,
        "priceYearly": p.price_yearly,
        "badge": p.badge,
        "highlight": p.highlight,
        "features": p.features or [],
        "buttonText": p.button_text
    }

def format_invoice_dict(b: BillingInvoice) -> dict:
    return {
        "id": b.id,
        "invoiceNumber": b.invoice_number,
        "date": b.date,
        "description": b.description,
        "amount": b.amount,
        "status": b.status,
        "paymentMethod": b.payment_method
    }

@router.get("/plans", response_model=List[dict])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SubscriptionPlan))
    plans = result.scalars().all()
    return [format_plan_dict(p) for p in plans]

@router.post("/checkout")
async def process_checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == req.planId))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    amount = plan.price_monthly if req.billingCycle == "monthly" else plan.price_yearly
    now = datetime.utcnow()
    inv_id = f"inv_{int(now.timestamp())}"
    inv_num = f"INV-{now.strftime('%Y')}-{int(now.timestamp()) % 10000:04d}"

    method_label = "MTN MoMo (*182#)" if req.paymentMethod == "momo" else "Credit Card (Visa/Mastercard)"

    new_invoice = BillingInvoice(
        id=inv_id,
        user_id=current_user.id,
        invoice_number=inv_num,
        date=now.strftime("%b %d, %Y"),
        description=f"{plan.name} — {req.billingCycle.capitalize()} Subscription",
        amount=f"{amount:,} RWF",
        status="Paid",
        payment_method=method_label
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)

    return {
        "success": True,
        "message": f"Successfully upgraded to {plan.name} via {method_label}",
        "invoice": format_invoice_dict(new_invoice)
    }

@router.get("/history", response_model=List[dict])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BillingInvoice)
        .where(BillingInvoice.user_id == current_user.id)
        .order_by(desc(BillingInvoice.created_at))
    )
    invoices = result.scalars().all()
    return [format_invoice_dict(b) for b in invoices]
