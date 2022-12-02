"""Handlers for juju controller."""
from contextlib import asynccontextmanager

from juju.controller import Controller


@asynccontextmanager
async def connect_controller(controller_name: str) -> Controller:
    """Handle connecting to and disconnecting from a Juju Controller."""
    controller = Controller(max_frame_size=2**64)
    if controller_name:
        await controller.connect(controller_name)
    else:
        await controller.connect()
    try:
        yield controller
    finally:
        await controller.disconnect()
