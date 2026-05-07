from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from api.dependencies.db import (
    get_db
)

from core.models.order import Order

from core.services.order_service import (
    OrderService
)

router = APIRouter()


@router.get("/api/order/otp/{order_id}")
async def get_order_otp(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Order).where(
            Order.id == order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order = await OrderService.update_otp(
        db,
        order
    )

    return {
        "otp": order.otp_code
    }


@router.post("/api/order/cancel/{order_id}")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Order).where(
            Order.id == order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    await OrderService.cancel_order(
        db,
        order
    )

    return {
        "status": "cancelled"
    }
