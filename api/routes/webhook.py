from datetime import datetime

from fastapi import (
    APIRouter,
    Request,
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

from core.models.payment_transaction import (
    PaymentTransaction
)

from core.services.paystack_service import (
    PaystackService
)

from core.services.wallet_service import (
    WalletService
)

router = APIRouter()


@router.post("/api/webhook/paystack")
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    payload = await request.body()

    signature = request.headers.get(
        "x-paystack-signature"
    )

    valid = (
        PaystackService.verify_webhook_signature(
            payload,
            signature
        )
    )

    if not valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    event = await request.json()

    if event["event"] != "charge.success":

        return {
            "status": "ignored"
        }

    data = event["data"]

    reference = data["reference"]

    result = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.reference
            == reference
        )
    )

    payment = result.scalar_one_or_none()

    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if payment.status == "completed":

        return {
            "status": "already_processed"
        }

    await WalletService.credit_balance(
        db=db,
        user_id=payment.user_id,
        amount=payment.amount,
        reference=payment.reference,
        description="Wallet funding"
    )

    payment.status = "completed"

    payment.paystack_data = data

    payment.completed_at = datetime.utcnow()

    await db.commit()

    return {
        "status": "success"
    }
