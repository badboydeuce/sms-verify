from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    DateTime
)

from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from core.database.base import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )

    type: Mapped[str] = mapped_column(
        String(20)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"
    )

    reference: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    description: Mapped[str] = mapped_column(
        String(500)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )