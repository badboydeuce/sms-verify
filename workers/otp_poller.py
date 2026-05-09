# workers/otp_poller.py

import asyncio
import logging

from aiogram import Bot
from sqlalchemy import select

from core.database.session import AsyncSessionLocal
from core.services.order_service import OrderService
from core.models.order import Order

logger = logging.getLogger(__name__)

MAX_WAIT_SECONDS = 300  # 5 minutes
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

                # Check if cancelled
                if order.status == "CANCELLED":
                    return

                order = await OrderService.update_otp(db, order)

                if order.otp_code:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"✅ <b>OTP Received</b>\n\nCode:\n<code>{order.otp_code}</code>",
                        parse_mode="HTML"
                    )
                    return

        except Exception as e:
            logger.error(f"poll_order error for order {order_id}: {e}")

        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    # Timed out — notify user
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
                "⏰ <b>OTP Timeout</b>\n\n"
                "No SMS received within 5 minutes.\n"
                "The number has expired."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"poll_order timeout handler error: {e}")
