from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from decimal import Decimal
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:

    # FIX: Using the exact attribute 'tenant_id' found in your logs
    tenant_id = getattr(current_user, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant identity not found")

    # This pulls from the isolated cache we fixed in cache.py
    revenue_data = await get_revenue_summary(property_id, tenant_id)

    # Financial precision fix for the finance team
    total_val = revenue_data.get('total', '0.00')
    total_revenue = Decimal(str(total_val))

    return {
        "property_id": revenue_data.get('property_id', property_id),
        "total_revenue": float(total_revenue),
        "currency": revenue_data.get('currency', 'USD'),
        "reservations_count": revenue_data.get('count', 0)
    }