from juju.controller import Controller

from juju_spell.commands.base import BaseJujuCommand

__all__ = ["AddUserCommand"]


class AddUserCommand(BaseJujuCommand):
    async def execute(self, controller: Controller, **kwargs):
        user = await controller.add_user(
            username=kwargs["username"],
            password=kwargs["password"],
            display_name=kwargs["display_name"],
        )

        return {
            "uuid": kwargs["controller_config"].uuid,
            "username": user.username,
            "display_name": user.display_name,
            "password": kwargs["password"],
        }
