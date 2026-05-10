# api/routes/admin.py

from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from core.services.user_service import UserService
from core.services.wallet_service import WalletService

router = APIRouter()


class CreditUserSchema(BaseModel):
    telegram_id: int
    amount: float


@router.get("/api/admin/stats")
async def admin_stats():
    return {
        "users": 0,
        "orders": 0,
        "revenue": 0
    }


@router.post("/api/admin/credit")
async def credit_user(
    payload: CreditUserSchema,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_user_by_telegram_id(db, payload.telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reference = f"admin_credit_{uuid4()}"

    new_balance = await WalletService.credit_balance(
        db=db,
        user_id=user.id,
        amount=Decimal(str(payload.amount)),
        reference=reference,
        description="Admin manual credit"
    )

    return {
        "telegram_id": payload.telegram_id,
        "amount": payload.amount,
        "new_balance": float(new_balance)
    }
