from typing import List

from juju.client._definitions import FullStatus
from juju.controller import Controller
from juju.model import Model

from multijuju.commands.base import BaseJujuCommand


async def get_model_status(model_name) -> FullStatus:

    model = Model()
    await model.connect_model(model_name=model_name)
    status = await model.get_status()
    return status


class StatusCommand(BaseJujuCommand):
    async def execute(self, controller: Controller, **kwargs) -> List[FullStatus]:
        results = []
        model_names = await controller.get_models()
        for model_name in model_names:
            if (kwargs["parsed_args"].models and model_names in kwargs["parsed_args"].models) or (
                not kwargs["parsed_args"].models
            ):
                results.append(await get_model_status(model_name=model_name))
        return results
