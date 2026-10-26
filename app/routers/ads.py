from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.ad import AdCampaign
from app.models.user import User
from app.schemas.all_schemas import AdCampaignCreateRequest
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/ads", tags=["Advertising Campaigns"])

def format_ad_dict(a: AdCampaign) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "audience": a.audience,
        "budgetRwf": a.budget_rwf,
        "spentRwf": a.spent_rwf,
        "startDate": a.start_date,
        "endDate": a.end_date,
        "status": a.status,
        "creativeUrl": a.creative_url,
        "impressions": a.impressions,
        "clicks": a.clicks,
        "ctr": a.ctr,
        "conversions": a.conversions,
        "cpcRwf": a.cpc_rwf
    }

@router.get("", response_model=List[dict])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AdCampaign).order_by(desc(AdCampaign.created_at)))
    ads = result.scalars().all()
    return [format_ad_dict(a) for a in ads]

@router.post("", response_model=dict)
async def create_campaign(
    req: AdCampaignCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ad_id = f"ad_{int(datetime.utcnow().timestamp())}"
    new_ad = AdCampaign(
        id=ad_id,
        user_id=current_user.id,
        title=req.title,
        description=req.description,
        audience=req.audience or "Tech & Business Professionals in Rwanda",
        budget_rwf=req.budgetRwf,
        spent_rwf=0,
        start_date=req.startDate or datetime.utcnow().strftime("%Y-%m-%d"),
        end_date=req.endDate,
        status="Active",
        creative_url=req.creativeUrl or "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
        impressions=0,
        clicks=0,
        ctr="0.00%",
        conversions=0,
        cpc_rwf=0
    )
    db.add(new_ad)
    await db.commit()
    await db.refresh(new_ad)
    return format_ad_dict(new_ad)

@router.patch("/{ad_id}/status")
async def update_campaign_status(
    ad_id: str,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AdCampaign).where(AdCampaign.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad campaign not found")
        
    ad.status = status
    await db.commit()
    return {"id": ad.id, "status": ad.status}
