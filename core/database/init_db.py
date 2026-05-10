# core/database/init_db.py

from core.database.session import engine
from core.database.base import Base

from core.models.user import User
from core.models.order import Order
from core.models.transaction import Transaction
from core.models.rental_sms import RentalSMS  # ✅ added


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
