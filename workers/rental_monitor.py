# workers/rental_monitor.py

import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from sqlalchemy import select

from core.database.session import AsyncSessionLocal
from core.models.order import Order
from core.models.rental_sms import RentalSMS
from core.services.smsman_service import SMSManService
from bot.keyboards.orders import rental_order_keyboard

logger = logging.getLogger(__name__)

POLL_INTERVAL = 3


def _format_order_text(order, sms_list):
    header = (
        f"<b>♻️ {order.service_name}</b>\n"
        f"📱 <code>{order.number}</code>\n"
        f"🌍 {order.country_name}\n"
        f"💰 ₦{order.cost}\n"
        f"⏱ {order.rental_duration}\n"
        f"📅 {order.created_at.strftime('%d %b %Y %H:%M')}\n"
    )

    if not sms_list:
        return header + "\n⏳ Waiting for SMS..."

    messages = "\n——————\n".join(
        f"💬 Message: {sms.message}\n🕐 Timestamp: {sms.received_at}"
        for sms in sms_list
    )

    return header + f"\n——————\n{messages}\n——————"


async def monitor_rental(
    bot: Bot,
    order_id: int,
    chat_id: int,
    message_id: int
):
    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
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
                            f"📱 <code>{order.number}</code>\n"
                            f"🌍 {order.country_name}\n"
                            f"Your rental period has ended."
                        ),
                        parse_mode="HTML"
                    )
                    return

                # Fetch SMS from SMS-Man
                response = await SMSManService.get_rental_sms(order.request_id)
                sms_list = response.get("sms", [])
                if isinstance(sms_list, dict):
                    sms_list = [sms_list]

                # Get existing SMS from DB
                existing = await db.execute(
                    select(RentalSMS).where(RentalSMS.order_id == order_id)
                )
                existing_messages = {s.message for s in existing.scalars().all()}

                # Save new SMS
                new_found = False
                for sms in sms_list:
                    msg = sms.get("message")
                    if msg and msg not in existing_messages:
                        db.add(RentalSMS(
                            order_id=order_id,
                            message=msg,
                            code=sms.get("code"),
                            received_at=sms.get("time", "")
                        ))
                        existing_messages.add(msg)
                        new_found = True

                if new_found:
                    await db.commit()

                # Fetch all SMS for display
                all_sms_result = await db.execute(
                    select(RentalSMS)
                    .where(RentalSMS.order_id == order_id)
                    .order_by(RentalSMS.created_at.asc())
                )
                all_sms = all_sms_result.scalars().all()

                if new_found:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=_format_order_text(order, all_sms),
                        reply_markup=rental_order_keyboard(order.id),
                        parse_mode="HTML"
                    )

        except Exception as e:
            logger.error(f"monitor_rental error for order {order_id}: {e}")

        await asyncio.sleep(POLL_INTERVAL)
