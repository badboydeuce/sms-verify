from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from core.models.transaction import Transaction


class WalletService:

    @staticmethod
    async def get_balance(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one()

        return user.balance

    @staticmethod
    async def credit_balance(
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        reference: str,
        description: str
    ):

        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .with_for_update()
        )

        user = result.scalar_one()

        user.balance += amount

        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            type="credit",
            status="completed",
            reference=reference,
            description=description
        )

        db.add(transaction)

        await db.commit()

        return user.balance

    @staticmethod
    async def debit_balance(
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        reference: str,
        description: str
    ):

        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .with_for_update()
        )

        user = result.scalar_one()

        if user.balance < amount:
            raise Exception(
                "Insufficient balance"
            )

        user.balance -= amount

        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            type="debit",
            status="completed",
            reference=reference,
            description=description
        )

        db.add(transaction)

        await db.commit()

        return user.balance