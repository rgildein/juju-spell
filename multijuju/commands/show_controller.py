import pprint

from craft_cli import emit
from juju.client._definitions import ControllerAPIInfoResults

from multijuju.commands.controller import connect_controller


def controller_info_formatter(info: ControllerAPIInfoResults):
    """Pretty formatter for controller information."""
    # TODO: pretty output
    return pprint.pformat(info.serialize())


async def cmd_show_controller(controller_name: str):
    """Get information from juju controller."""
    async with connect_controller(controller_name) as controller:
        info = await controller.info()
        emit.message(controller_info_formatter(info))
