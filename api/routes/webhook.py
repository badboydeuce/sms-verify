# api/routes/webhook.py

import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from core.models.transaction import Transaction
from core.services.paystack_service import PaystackService
from core.services.wallet_service import WalletService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/webhook/paystack")
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature")

    # ✅ Fix 1 — signature guard
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    valid = PaystackService.verify_webhook_signature(payload, signature)

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = await request.json()

    if event["event"] != "charge.success":
        return {"status": "ignored"}

    data = event["data"]
    reference = data["reference"]

    # ✅ Fix 2 — lock row to prevent double credit
    result = await db.execute(
        select(Transaction)
        .where(Transaction.reference == reference)
        .with_for_update()  # ✅ row-level lock
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # ✅ Fix 2 — idempotency check before crediting
    if payment.status == "completed":
        logger.info(f"Webhook: already processed {reference}")
        return {"status": "already_processed"}

    await WalletService.credit_balance(
        db=db,
        user_id=payment.user_id,
        amount=payment.amount,
        reference=payment.reference,
        description="Wallet funding"
    )

    payment.status = "completed"
    await db.commit()

    logger.info(f"Webhook: credited wallet for reference {reference}")
    return {"status": "success"}


# ====================== CALLBACK (browser redirect) ======================
@router.get("/webhook/paystack")
async def paystack_callback(
    trxref: str,
    reference: str,
    db: AsyncSession = Depends(get_db)
):
    # ✅ Fix 3 — lock row same as webhook to prevent race condition
    result = await db.execute(
        select(Transaction)
        .where(Transaction.reference == reference)
        .with_for_update()
    )
    payment = result.scalar_one_or_none()

    if not payment:
        return JSONResponse(
            content={"message": "Payment not found"},
            media_type="application/json; charset=utf-8"
        )

    # ✅ Fix 3 — check status before crediting
    if payment.status == "completed":
        return JSONResponse(
            content={"message": "✅ Payment already processed. Check your wallet balance."},
            media_type="application/json; charset=utf-8"
        )

    # Verify with Paystack directly
    try:
        response = await PaystackService.verify_transaction(reference)
    except Exception as e:
        logger.error(f"Paystack verify failed: {e}")
        return JSONResponse(
            content={"message": "❌ Could not verify payment. Try again."},
            media_type="application/json; charset=utf-8"
        )

    if response["data"]["status"] != "success":
        return JSONResponse(
            content={"message": "❌ Payment verification failed."},
            media_type="application/json; charset=utf-8"
        )

    # ✅ Fix 3 — re-check status after Paystack verify (webhook may have processed it)
    await db.refresh(payment)
    if payment.status == "completed":
        return JSONResponse(
            content={"message": "✅ Payment already processed. Check your wallet balance."},
            media_type="application/json; charset=utf-8"
        )

    await WalletService.credit_balance(
        db=db,
        user_id=payment.user_id,
        amount=payment.amount,
        reference=payment.reference,
        description="Wallet funding"
    )

    payment.status = "completed"
    await db.commit()

    logger.info(f"Callback: credited wallet for reference {reference}")
    return JSONResponse(
        content={"message": "✅ Payment successful! Your wallet has been funded."},
        media_type="application/json; charset=utf-8"
    )
