import asyncio


async def rental_monitor():

    while True:

        print("checking rentals")

        await asyncio.sleep(30)