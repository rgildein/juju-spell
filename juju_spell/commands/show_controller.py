from juju.client._definitions import ControllerAPIInfoResults
from juju.controller import Controller

from juju_spell.commands.base import BaseJujuCommand


class ShowControllerCommand(BaseJujuCommand):
    """Command to show a controller."""

    async def execute(self, controller: Controller, **kwargs) -> ControllerAPIInfoResults:
        """Execute main code.

        Changed name because this has to override base_command.
        """
        return await controller.info()
