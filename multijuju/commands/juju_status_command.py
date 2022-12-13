from juju.controller import Controller
from juju.model import Model

from multijuju.commands.base import BaseJujuCommand


class JujuStatusCommand(BaseJujuCommand):
    async def execute(self, controller: Controller, **kwargs):
        model_uuids = await controller.model_uuids()
        model = Model()
        first, *rest = model_uuids
        await model.connect_model(model_name=first)
        status = await model.get_status()
        return status
