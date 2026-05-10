# workers/rental_monitor.py

import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from sqlalchemy import select

from core.database.session import AsyncSessionLocal
from core.models.order import Order
from core.services.smsman_service import SMSManService
from bot.keyboards.orders import rental_order_keyboard

logger = logging.getLogger(__name__)

POLL_INTERVAL = 30


async def monitor_rental(
    bot: Bot,
    order_id: int,
    chat_id: int,
    message_id: int
):
    seen_messages = set()

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
                    logger.error(f"monitor_rental: order {order_id} not found")
                    return

                if order.status in ("CANCELLED", "EXPIRED", "COMPLETED"):
                    return

                if order.expires_at and datetime.utcnow() > order.expires_at:
                    order.status = "EXPIRED"
                    await db.commit()
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=(
                            f"⏰ <b>Rental Expired</b>\n\n"
                            f"📱 Number: <code>{order.number}</code>\n"
                            f"Your rental period has ended."
                        ),
                        parse_mode="HTML"
                    )
                    return

                # Poll SMS-Man for all SMS
                response = await SMSManService.get_rental_sms(order.request_id)

                sms_list = response.get("sms", [])
                if isinstance(sms_list, dict):
                    sms_list = [sms_list]

                # Find new messages
                new_messages = [
                    sms for sms in sms_list
                    if sms.get("message") and sms.get("message") not in seen_messages
                ]

                if new_messages:
                    for sms in new_messages:
                        seen_messages.add(sms["message"])

                    # Build SMS display
                    sms_text = "\n==============\n".join(
                        f"📩 {sms['message']}\n🕐 {sms.get('time', '')}"
                        for sms in sms_list
                        if sms.get("message")
                    )

                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=(
                            f"<b>♻️ Rental Number Active</b>\n\n"
                            f"📱 Number:\n<code>{order.number}</code>\n\n"
                            f"🌍 Country: {order.country_name}\n"
                            f"⏱ Duration: {order.rental_duration}\n\n"
                            f"<b>📨 Messages:</b>\n\n"
                            f"{sms_text}"
                        ),
                        reply_markup=rental_order_keyboard(order.id),
                        parse_mode="HTML"
                    )

        except Exception as e:
            logger.error(f"monitor_rental error for order {order_id}: {e}")

        await asyncio.sleep(POLL_INTERVAL)
