from pydantic import BaseModel
from decimal import Decimal


class FundWalletSchema(BaseModel):

    telegram_id: int

    amount: Decimal
