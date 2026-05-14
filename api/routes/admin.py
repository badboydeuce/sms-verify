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
from core.models.transaction import Transaction

from sqlalchemy import select, func, cast
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

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
async def admin_stats(db: AsyncSession = Depends(get_db)):

    # Total users
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0

    # Total orders
    orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = orders_result.scalar() or 0

    # Total revenue — cast string to enum type for comparison
    revenue_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.type == "DEBIT",
            Transaction.status == cast(
                "completed",
                PgEnum(name="transactionstatus")
            )
        )
    )
    total_revenue = float(revenue_result.scalar() or 0)

    # Total wallet balance
    balance_result = await db.execute(select(func.sum(User.balance)))
    total_wallet_balance = float(balance_result.scalar() or 0)

    # Orders breakdown by status
    status_result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    orders_by_status = {row[0]: row[1] for row in status_result.fetchall()}

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_wallet_balance": total_wallet_balance,
        "orders_by_status": orders_by_status
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
