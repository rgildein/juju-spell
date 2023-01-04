from juju.controller import Controller

from juju_spell.commands.base import BaseJujuCommand


class PingCommand(BaseJujuCommand):
    async def execute(self, controller: Controller, **kwargs) -> str:
        """Check if controller is connected."""
        return "accessible" if controller.is_connected() else "unreachable"
