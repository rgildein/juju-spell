"""Module that provides functions to assist asynchronous execution."""
import asyncio


def run_async(*tasks):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(asyncio.gather(*tasks))
