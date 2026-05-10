# core/models/rental_sms.py

from sqlalchemy import String, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from core.database.base import Base


class RentalSMS(Base):

    __tablename__ = "rental_sms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    received_at: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
