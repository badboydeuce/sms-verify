# core/models/transaction.py

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from datetime import datetime
import enum

from core.database.base import Base


class TransactionType(str, enum.Enum):
    credit = "CREDIT"
    debit = "DEBIT"


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

    type: Mapped[str] = mapped_column(
        PgEnum("CREDIT", "DEBIT", name="transactiontype", create_type=False),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        PgEnum("pending", "completed", "failed", name="transactionstatus", create_type=False),
        default="pending"
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
