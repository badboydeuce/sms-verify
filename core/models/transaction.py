# core/models/transaction.py

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import enum

from core.database.base import Base


class TransactionType(str, enum.Enum):
    credit = "credit"
    debit = "debit"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Transaction(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transactiontype"),  # ✅ matches DB enum name
        nullable=False
    )

    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transactionstatus"),
        default=TransactionStatus.pending
    )

    reference: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
