# workers/otp_poller.py

import asyncio
import logging

from aiogram import Bot
from sqlalchemy import select

from core.database.session import AsyncSessionLocal
from core.services.order_service import OrderService
from core.models.order import Order

logger = logging.getLogger(__name__)

MAX_WAIT_SECONDS = 300
POLL_INTERVAL = 5


async def poll_order(
    bot: Bot,
    order_id: int,
    chat_id: int,
    message_id: int
):
    elapsed = 0

    while elapsed < MAX_WAIT_SECONDS:

        try:
            async with AsyncSessionLocal() as db:

                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
                    logger.error(f"poll_order: order {order_id} not found")
                    return

                if order.status == "CANCELLED":
                    return

                order = await OrderService.update_otp(db, order)

                if order.sms_received:
                    sms_text = getattr(order, "sms_text", None) or order.otp_code
                    extra_charge = getattr(order, "extra_charge", None)

                    # Build charge info line
                    if extra_charge:
                        charge_info = (
                            f"\n\n⚠️ <b>Service Charge Notice</b>\n"
                            f"OTP was delivered by <b>{extra_charge['service']}</b>\n"
                            f"Total charged: ₦{extra_charge['amount']}\n"
                            f"Extra deducted: ₦{extra_charge['difference']}"
                        )
                    else:
                        charge_info = f"\n\n💰 Charged: ₦{order.cost}"

                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=(
                            f"✅ <b>SMS Received</b>\n\n"
                            f"📱 Number: <code>{order.number}</code>\n"
                            f"📦 Service: {order.service_name}"
                            f"{charge_info}\n\n"
                            f"💬 Message:\n<code>{sms_text}</code>"
                        ),
                        parse_mode="HTML"
                    )
                    return

        except Exception as e:
            logger.error(f"poll_order error for order {order_id}: {e}")

        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    # Timed out
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            if order and order.status == "PENDING":
                order.status = "EXPIRED"
                await db.commit()

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                "⏰ <b>No SMS Received</b>\n\n"
                "The number expired after 5 minutes.\n"
                "Please try another number."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"poll_order timeout handler error: {e}")
