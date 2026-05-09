# core/services/wallet_service.py

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
            select(User).where(User.id == user_id)
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

        # ✅ Update existing transaction instead of inserting a new one
        tx_result = await db.execute(
            select(Transaction).where(Transaction.reference == reference)
        )
        transaction = tx_result.scalar_one_or_none()

        if transaction:
            transaction.status = "completed"
            transaction.description = description
        else:
            # Fallback: insert if not found
            db.add(Transaction(
                user_id=user_id,
                amount=amount,
                type="CREDIT",
                status="completed",
                reference=reference,
                description=description
            ))

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
            raise Exception("Insufficient balance")

        user.balance -= amount

        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            type="DEBIT",
            status="completed",
            reference=reference,
            description=description
        )

        db.add(transaction)
        await db.commit()

        return user.balance
