# core/services/order_service.py

from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.order import Order
from core.services.wallet_service import WalletService
from core.services.smsman_service import SMSManService
from core.exceptions.smsman import SMSManAPIError, NumberUnavailable
from core.exceptions.wallet import InsufficientBalance

logger = logging.getLogger(__name__)


def _calculate_rental_expiry(rent_type: str, time: int) -> datetime:
    now = datetime.utcnow()
    if rent_type == "hour":
        return now + timedelta(hours=time)
    elif rent_type == "day":
        return now + timedelta(days=time)
    elif rent_type == "week":
        return now + timedelta(weeks=time)
    elif rent_type == "month":
        return now + timedelta(days=30 * time)
    return now + timedelta(hours=time)


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
        final_price = price
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

        logger.info(f"SMS-Man activation response: {smsman_response}")

        if "error_code" in smsman_response:
            error_code = smsman_response["error_code"]
            error_msg = smsman_response.get("error_msg", error_code)

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

        if "request_id" not in smsman_response or "number" not in smsman_response:
            await WalletService.credit_balance(
                db=db,
                user_id=user_id,
                amount=final_price,
                reference=f"refund_{reference}",
                description="Refund: unexpected SMS-Man response"
            )
            raise SMSManAPIError("Unexpected SMS-Man response")

        order = Order(
            user_id=user_id,
            order_type="ACTIVATION",
            service_id=service_id,
            service_name=service_name,
            country_id=country_id,
            country_name=country_name,
            number=smsman_response["number"],
            request_id=str(smsman_response["request_id"]),
            cost=final_price,
            status="PENDING",
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
        final_price = price
        reference = str(uuid4())

        await WalletService.debit_balance(
            db=db,
            user_id=user_id,
            amount=final_price,
            reference=reference,
            description="Rental number purchase"
        )

        try:
            smsman_response = await SMSManService.rent_number(
                country_id,
                rent_type,
                time
            )

            print(f"RENTAL ORDER RESPONSE: {smsman_response}", flush=True)
            logger.info(f"SMS-Man rental response: {smsman_response}")

            if "error_code" in smsman_response:
                raise SMSManAPIError(
                    smsman_response.get("error_msg", "Rental failed")
                )

            if "balance" in smsman_response:
                raise SMSManAPIError(
                    smsman_response.get("balance", "Insufficient SMS-Man balance")
                )

            if "request_id" not in smsman_response or "number" not in smsman_response:
                raise SMSManAPIError(
                    f"Unexpected rental response: {smsman_response}"
                )

            order = Order(
                user_id=user_id,
                order_type="RENTAL",
                service_id="rental",
                service_name="Rental Number",
                country_id=country_id,
                country_name=country_name,
                number=smsman_response["number"],
                request_id=str(smsman_response["request_id"]),
                cost=final_price,
                status="PENDING",
                rental_duration=f"{time} {rent_type}",
                expires_at=_calculate_rental_expiry(rent_type, time)
            )

            db.add(order)
            await db.commit()
            await db.refresh(order)

            return order

        except SMSManAPIError:
            await WalletService.credit_balance(
                db=db,
                user_id=user_id,
                amount=final_price,
                reference=f"refund_{reference}",
                description="Refund: rental number failed"
            )
            raise

        except Exception as e:
            logger.error(f"create_rental_order unexpected error: {e}")
            try:
                await WalletService.credit_balance(
                    db=db,
                    user_id=user_id,
                    amount=final_price,
                    reference=f"refund_{reference}",
                    description="Refund: rental order creation failed"
                )
            except Exception as refund_error:
                logger.error(f"Refund also failed: {refund_error}")
            raise SMSManAPIError(f"Rental failed: {str(e)}")

    @staticmethod
    async def update_otp(
        db: AsyncSession,
        order: Order
    ):
        response = await SMSManService.get_activation_sms(order.request_id)

        print(f"SMS-MAN RESPONSE: {response}", flush=True)
        logger.info(f"SMS-Man get_sms response: {response}")

        if response.get("error_code") == "wait_sms":
            return order

        sms_text = (
            response.get("sms_text")
            or response.get("msg")
            or response.get("sms_code")
        )
        sms_code = response.get("sms_code")

        if sms_text:
            delivered_application_id = str(response.get("application_id", ""))
            ordered_application_id = str(order.service_id)

            extra_charge = None

            # ✅ Check if a different service delivered the SMS
            if delivered_application_id and delivered_application_id != ordered_application_id:
                logger.info(
                    f"Service mismatch: ordered {ordered_application_id}, "
                    f"delivered {delivered_application_id}"
                )

                try:
                    prices = await SMSManService.get_prices(order.country_id)

                    delivered_service = next(
                        (
                            p for p in prices
                            if str(p["application_id"]) == delivered_application_id
                        ),
                        None
                    )

                    if delivered_service:
                        delivered_price = Decimal(
                            str(SMSManService.apply_markup(
                                float(delivered_service["price"])
                            ))
                        )

                        # Only charge extra if delivered price is higher
                        if delivered_price > order.cost:
                            difference = delivered_price - order.cost

                            await WalletService.debit_balance(
                                db=db,
                                user_id=order.user_id,
                                amount=difference,
                                reference=str(uuid4()),
                                description=(
                                    f"Extra charge: OTP delivered by "
                                    f"{delivered_service['application']} "
                                    f"instead of {order.service_name}"
                                )
                            )

                            extra_charge = {
                                "service": delivered_service["application"],
                                "amount": delivered_price,
                                "difference": difference
                            }

                            logger.info(
                                f"Extra charge of ₦{difference} applied "
                                f"to user {order.user_id}"
                            )

                except Exception as e:
                    logger.error(f"Failed to apply extra charge: {e}")

            order.otp_code = sms_code or sms_text
            order.sms_received = True
            order.status = "RECEIVED"
            await db.commit()

            order.sms_text = sms_text
            order.extra_charge = extra_charge  # attach for display in poller

        return order

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order: Order
    ):
        order.status = "CANCELLED"
        await db.commit()
        return order
