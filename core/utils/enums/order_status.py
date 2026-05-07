from enum import Enum


class OrderStatus(str, Enum):

    PENDING = "pending"

    RECEIVED = "received"

    ACTIVE = "active"

    COMPLETED = "completed"

    CANCELLED = "cancelled"

    EXPIRED = "expired"