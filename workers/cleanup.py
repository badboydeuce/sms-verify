# workers/cleanup.py

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, delete

from core.database.session import AsyncSessionLocal
from core.models.order import Order
from core.models.rental_sms import RentalSMS

logger = logging.getLogger(__name__)


async def cleanup_worker():
    while True:
        try:
            async with AsyncSessionLocal() as db:
                cutoff = datetime.utcnow() - timedelta(hours=24)

                # Find orders expired more than 24hrs ago
                result = await db.execute(
                    select(Order).where(
                        Order.status == "EXPIRED",
                        Order.expires_at <= cutoff
                    )
                )
                expired_orders = result.scalars().all()

                for order in expired_orders:
                    # Delete rental SMS first
                    await db.execute(
                        delete(RentalSMS).where(
                            RentalSMS.order_id == order.id
                        )
                    )
                    await db.delete(order)
                    logger.info(f"Cleaned up expired order {order.id}")

                await db.commit()

        except Exception as e:
            logger.error(f"cleanup_worker error: {e}")

        await asyncio.sleep(3600)  # run every hour
