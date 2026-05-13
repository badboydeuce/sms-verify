# api/routes/admin.py

from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from core.services.user_service import UserService
from core.services.wallet_service import WalletService
from core.models.user import User
from core.models.order import Order

router = APIRouter()


class CreditUserSchema(BaseModel):
    telegram_id: int
    amount: float


class DebitUserSchema(BaseModel):
    telegram_id: int
    amount: float


class BroadcastSchema(BaseModel):
    message: str


# ====================== STATS ======================
@router.get("/api/admin/stats")
async def admin_stats():
    return {
        "users": 0,
        "orders": 0,
        "revenue": 0
    }


# ====================== CREDIT USER ======================
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


# ====================== DEBIT USER ======================
@router.post("/api/admin/debit")
async def debit_user(
    payload: DebitUserSchema,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_user_by_telegram_id(db, payload.telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.balance < Decimal(str(payload.amount)):
        raise HTTPException(status_code=400, detail="Insufficient balance")

    reference = f"admin_debit_{uuid4()}"

    new_balance = await WalletService.debit_balance(
        db=db,
        user_id=user.id,
        amount=Decimal(str(payload.amount)),
        reference=reference,
        description="Admin manual debit"
    )

    return {
        "telegram_id": payload.telegram_id,
        "amount": payload.amount,
        "new_balance": float(new_balance)
    }


# ====================== VIEW USER ======================
@router.get("/api/admin/user/{telegram_id}")
async def get_user(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_user_by_telegram_id(db, telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count total orders
    result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == user.id)
    )
    total_orders = result.scalar() or 0

    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "balance": float(user.balance),
        "total_orders": total_orders,
        "is_admin": user.is_admin,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M UTC")
    }


# ====================== BROADCAST ======================
@router.post("/api/admin/broadcast")
async def broadcast_message(
    payload: BroadcastSchema,
    db: AsyncSession = Depends(get_db)
):
    # Fetch all user telegram_ids
    result = await db.execute(select(User.telegram_id))
    telegram_ids = result.scalars().all()

    if not telegram_ids:
        raise HTTPException(status_code=404, detail="No users found")

    return {
        "status": "queued",
        "total_users": len(telegram_ids),
        "telegram_ids": telegram_ids,
        "message": payload.message
    }
