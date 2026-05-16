# bot/main.py

import asyncio
import logging
from asyncio import create_task

from bot.loader import dp, bot
from bot.middlewares.user import UserMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

from bot.handlers.start import router as start_router
from bot.handlers.wallet import router as wallet_router
from bot.handlers.buy import router as buy_router
from bot.handlers.orders import router as orders_router
from bot.handlers.profile import router as profile_router
from bot.handlers.support import router as support_router
from bot.handlers.admin import router as admin_router

from workers.cleanup import cleanup_worker

logger = logging.getLogger(__name__)


# ====================== RESUME PENDING 5SIM ORDERS ======================
async def resume_pending_fivesim_orders(bot):
    from sqlalchemy import select
    from core.database.session import AsyncSessionLocal
    from core.models.order import Order
    from bot.handlers.buy import poll_fivesim_order

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(
                    Order.provider == "5sim",
                    Order.status == "PENDING",
                    Order.chat_id.isnot(None),
                    Order.message_id.isnot(None)
                )
            )
            pending = result.scalars().all()

        for order in pending:
            create_task(poll_fivesim_order(
                bot=bot,
                fivesim_order_id=int(order.service_id),
                chat_id=order.chat_id,
                message_id=order.message_id
            ))

        if pending:
            logger.info(f"Resumed {len(pending)} pending 5sim orders")

    except Exception as e:
        logger.error(f"resume_pending_fivesim_orders failed: {e}")


async def main():
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(ThrottlingMiddleware())

    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(buy_router)
    dp.include_router(orders_router)
    dp.include_router(profile_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)

    # ✅ Resume any pending 5sim orders from before restart
    await resume_pending_fivesim_orders(bot)

    # ✅ Start cleanup worker
    create_task(cleanup_worker())

    logger.info("Starting bot polling...")

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot shutting down...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
