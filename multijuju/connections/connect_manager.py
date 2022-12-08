from typing import Any, Dict

from juju import juju


class ConnectManager(object):
    """Connect manager is used to define connections for controllers.

    Usage example:
    async def task(...):
        ...
        connect_manager = ConnectManager():
        controller = await connect_manager.get_controller(controller_config)
        ...
    """

    _manager = None
    _controllers = {}

    def __new__(cls):
        if getattr(cls, "_manager") is None:
            cls._manager = super(ConnectManager, cls).__new__(cls)

        return cls._manager

    @property
    def controllers(self) -> Dict[str, juju.Controller]:
        """Return list of controllers ."""
        return self._controllers

    async def clean(self):
        """Close all connections."""
        for controller in self.controllers.values():
            await controller.disconnect()

    async def get_controller(
        self, config: Dict[str, Any()], sshuttle: bool = False, reconnect: bool = False
    ) -> juju.Controller:
        """Get controller."""
        controller = self.controllers.get(config["name"])
        if controller is None:
            controller = await self.get_controller(config, sshuttle)
        elif reconnect:
            await controller.disconnect()
            controller = await self.get_controller(config, sshuttle)

        # TODO: add connection validation and reconnect if it's needed
        return controller

    async def connect(self, config: Dict[str, Any()], sshuttle: bool = False) -> juju.Controller:
        """Prepare connection to Controller and return it."""
        controller = juju.Controller()
        # TODO: preparation connection to remote controller (sshuttle, port-forwarding)
        # TODO: add "localhost:<port>" to controllers api-endpoints
        await controller.connect(
            endpoint=config["api-endpoints"],
            uuid=config["uuid"],
            username=config["account"]["user"],
            password=config["account"]["password"],
            cacert=config["ca-cert"],
        )
        self.controllers[config["name"]] = controller
        return controller


get_controller = ConnectManager().get_controller
