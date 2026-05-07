from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    DateTime,
    JSON
)

from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from core.database.base import Base


class PaymentTransaction(Base):

    __tablename__ = "payment_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    reference: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"
    )

    paystack_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )