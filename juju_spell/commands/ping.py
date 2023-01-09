from juju.controller import Controller

from juju_spell.commands.base import BaseJujuCommand


class PingCommand(BaseJujuCommand):
    async def execute(self, controller: Controller, **kwargs) -> str:
        """Check if controller is connected."""
        connected = controller.is_connected()
        self.logger.debug(
            "controller %s(%s) is connected '%r'", controller.controller_name, controller.controller_uuid, connected
        )
        return "accessible" if connected else "unreachable"
