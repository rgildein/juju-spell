from juju.client._definitions import FullStatus
from juju.controller import Controller
from juju.model import Model

from multijuju.commands.base import BaseJujuCommand, CommandTarget


class StatusCommand(BaseJujuCommand):
    @staticmethod
    def target():
        return CommandTarget.MODEL

    async def execute(self, controller: Controller, model: Model, **kwargs) -> FullStatus:
        return await model.get_status()
