from typing import Dict

from juju import juju

from multijuju.config import Config


class ConnectManager:
    """Connect manager is used to define connections for controllers.

    Usage example:
    async def task(connect_manager, ...):
        ...
        async with connect_manager:
           controller = await connect_manager.connect("<controller-name>")
           ...


    def main():
        ...
        config = ...
        connect_manager = ConnectManger(config)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task(conn, ...))
    """

    def __init__(self, config: Config) -> None:
        """Initialize the ConnectManager."""
        self._config = config
        self._connections = {}

    async def __aenter__(self) -> "ConnectManager":
        """Enter ConnectManager."""
        return self

    async def __aexit__(self, *args):
        """Leave ConnectManager."""
        await self.clean()

    @property
    def config(self) -> Config:
        """Get config."""
        return self._config

    @property
    def connections(self) -> Dict[str, juju.Controller]:
        """Return list of controllers ."""
        return self._connections

    async def clean(self):
        """Close all connections."""
        for controller in self.connections.values():
            await controller.disconnect()

    async def connect(self, name: str, sshuttle: bool = False) -> juju.Controller:
        """Prepare connection to Controller and return it."""
        _ = self.config.get(name)
        # TODO: preparation connection to remote controller (sshuttle, port-forwarding)
        controller = juju.Controller()  # TODO: use JUJU_DATA or pass all information
        await controller.connect(name)
        return controller

    async def disconnect(self, name: str) -> None:
        """Disconnect controller."""
        controller = self.connections.get(name)
        if controller is None:
            raise KeyError(f"Connection to controllers {name} is not established.")

        await controller.disconnect()
