# core/models/user.py

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    Numeric,
    DateTime
)

from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from core.database.base import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,          # ✅ was default Integer
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
