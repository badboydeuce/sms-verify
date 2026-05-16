# core/models/order.py

from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    DateTime,
    Boolean,
    Integer,
    BigInteger
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from core.database.base import Base


class Order(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    order_type: Mapped[str] = mapped_column(
        PgEnum("ACTIVATION", "RENTAL", name="ordertype", create_type=False),
        nullable=False
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        default="smsman",
        nullable=False,
        server_default="smsman"
    )

    service_id: Mapped[str] = mapped_column(String(100))
    service_name: Mapped[str] = mapped_column(String(255))
    country_id: Mapped[str] = mapped_column(String(50))
    country_name: Mapped[str] = mapped_column(String(255))
    number: Mapped[str] = mapped_column(String(255))

    request_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    cost: Mapped[float] = mapped_column(Numeric(12, 2))

    status: Mapped[str] = mapped_column(
        PgEnum("PENDING", "RECEIVED", "EXPIRED", "CANCELLED", "COMPLETED", name="orderstatus", create_type=False),
        default="PENDING"
    )

    otp_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sms_received: Mapped[bool] = mapped_column(Boolean, default=False)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    rental_duration: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ✅ For resuming polls after bot restart
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
