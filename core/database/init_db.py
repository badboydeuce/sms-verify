# core/database/init_db.py

from core.database.session import engine
from core.database.base import Base

from core.models.user import User
from core.models.order import Order
from core.models.transaction import Transaction
# ❌ Remove this line — file no longer exists
# from core.models.payment_transaction import PaymentTransaction


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
