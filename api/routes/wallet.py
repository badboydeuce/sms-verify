# api/routes/wallet.py

from uuid import uuid4
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.wallet import FundWalletSchema
from api.dependencies.db import get_db
from core.validators.amount import validate_funding_amount
from core.services.user_service import UserService
from core.services.paystack_service import PaystackService
from core.models.transaction import Transaction, TransactionType, TransactionStatus

router = APIRouter()


@router.post("/api/wallet/fund")
async def fund_wallet(
    payload: FundWalletSchema,
    db: AsyncSession = Depends(get_db)
):
    validate_funding_amount(payload.amount)

    user = await UserService.get_user_by_telegram_id(db, payload.telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reference = str(uuid4())

    payment = Transaction(
        user_id=user.id,
        reference=reference,
        amount=Decimal(str(payload.amount)),
        type=TransactionType.credit,        # ✅ was "credit"
        status=TransactionStatus.pending,   # ✅ was "pending"
        description="Wallet funding via Paystack"
    )

    db.add(payment)
    await db.commit()

    response = await PaystackService.initialize_transaction(
        email=f"{user.telegram_id}@deuceverify.com",
        amount=int(payload.amount * 100),
        reference=reference,
        metadata={
            "telegram_id": user.telegram_id,
            "user_id": user.id
        }
    )

    return {
        "authorization_url": response["data"]["authorization_url"],
        "reference": reference
    }
