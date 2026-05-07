import asyncio

from aiogram import Bot

from core.database.session import (
    AsyncSessionLocal
)

from core.services.order_service import (
    OrderService
)

from sqlalchemy import select

from core.models.order import Order


async def poll_order(
    bot: Bot,
    order_id: int,
    chat_id: int,
    message_id: int
):

    while True:

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(Order).where(
                    Order.id == order_id
                )
            )

            order = result.scalar_one()

            order = (
                await OrderService.update_otp(
                    db,
                    order
                )
            )

            if order.otp_code:

                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"""
✅ OTP Received

Code:
<code>{order.otp_code}</code>
"""
                )

                return

        await asyncio.sleep(5)
