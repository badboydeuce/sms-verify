import asyncio

from core.smsman.activation import SMSManActivation


async def poll_otp(order):

    while True:

        response = await SMSManActivation.get_sms(
            order.request_id
        )

        print(response)

        await asyncio.sleep(5)