import asyncio


async def cleanup_worker():

    while True:

        print("cleaning expired orders")

        await asyncio.sleep(60)