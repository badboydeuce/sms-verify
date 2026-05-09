# core/services/order_service.py

from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.order import Order
from core.services.wallet_service import WalletService
from core.services.smsman_service import SMSManService
from core.exceptions.smsman import SMSManAPIError, NumberUnavailable
from core.exceptions.wallet import InsufficientBalance


class OrderService:

    @staticmethod
    async def create_activation_order(
        db: AsyncSession,
        user_id: int,
        country_id: str,
        country_name: str,
        service_id: str,
        service_name: str,
        price: Decimal
    ):
        final_price = Decimal(
            SMSManService.apply_markup(float(price))
        )

        reference = str(uuid4())

        await WalletService.debit_balance(
            db=db,
            user_id=user_id,
            amount=final_price,
            reference=reference,
            description=f"{service_name} activation"
        )

        smsman_response = await SMSManService.buy_activation_number(
            country_id,
            service_id
        )

        # ✅ SMS-Man returns error_code on failure, not a "success" key
        if "error_code" in smsman_response:
            error_code = smsman_response["error_code"]
            error_msg = smsman_response.get("error_msg", error_code)

            # Refund the deducted balance
            await WalletService.credit_balance(
                db=db,
                user_id=user_id,
                amount=final_price,
                reference=f"refund_{reference}",
                description=f"Refund: {service_name} activation failed"
            )

            if error_code == "no_numbers":
                raise NumberUnavailable(error_msg)

            raise SMSManAPIError(error_msg)

        # ✅ Success — response contains request_id and number
        if "request_id" not in smsman_response or "number" not in smsman_response:
            await WalletService.credit_balance(
                db=db,
                user_id=user_id,
                amount=final_price,
                reference=f"refund_{reference}",
                description=f"Refund: unexpected SMS-Man response"
            )
            raise SMSManAPIError("Unexpected SMS-Man response")

        order = Order(
            user_id=user_id,
            order_type="activation",
            service_id=service_id,
            service_name=service_name,
            country_id=country_id,
            country_name=country_name,
            number=smsman_response["number"],
            request_id=smsman_response["request_id"],
            cost=final_price,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(minutes=20)
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def create_rental_order(
        db: AsyncSession,
        user_id: int,
        country_id: str,
        country_name: str,
        rent_type: str,
        time: int,
        price: Decimal
    ):
        final_price = Decimal(
            SMSManService.apply_markup(float(price))
        )

        reference = str(uuid4())

        await WalletService.debit_balance(
            db=db,
            user_id=user_id,
            amount=final_price,
            reference=reference,
            description="Rental number purchase"
        )

        smsman_response = await SMSManService.rent_number(
            country_id,
            rent_type,
            time
        )

        if "error_code" in smsman_response:
            await WalletService.credit_balance(
                db=db,
                user_id=user_id,
                amount=final_price,
                reference=f"refund_{reference}",
                description="Refund: rental number failed"
            )
            raise SMSManAPIError(smsman_response.get("error_msg", "Rental failed"))

        order = Order(
            user_id=user_id,
            order_type="rental",
            service_id="rental",
            service_name="Rental Number",
            country_id=country_id,
            country_name=country_name,
            number=smsman_response["number"],
            request_id=smsman_response["request_id"],
            cost=final_price,
            status="active",
            rental_duration=f"{time} {rent_type}"
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def update_otp(
        db: AsyncSession,
        order: Order
    ):
        response = await SMSManService.get_activation_sms(order.request_id)

        code = response.get("sms_code")

        if code:
            order.otp_code = code
            order.sms_received = True
            order.status = "received"
            await db.commit()

        return order

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order: Order
    ):
        order.status = "cancelled"
        await db.commit()
        return order
