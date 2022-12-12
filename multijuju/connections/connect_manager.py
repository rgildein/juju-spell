import dataclasses
import socket
import subprocess
from typing import Any, Dict, List, Optional

from juju import juju


def get_free_tcp_port() -> int:
    """Get free TCP port."""
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port


def ssh_port_forwarding_proc(
    local_target: str, remote_target: str, destination: str, jumps: Optional[List[str]] = None
) -> subprocess.Popen:
    """Port forward target through destination."""
    jumps_option = " ".join(f"-J {jump}" for jump in jumps)
    cmd = ["ssh", "-N", "-L", f"{local_target}:{remote_target}", f"{jumps_option}", f"{destination}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def sshuttle_proc(destination: str, subnets: List[str], jumps: Optional[List[str]] = None) -> subprocess.Popen:
    """Create sshuttle tunnels."""
    extra_options = []
    if jumps:
        jumps_option = " ".join(f"-J {jump}" for jump in jumps)
        extra_options.append(f"-e 'ssh {jumps_option}'")

    subnet_options = " ".join(subnets)
    cmd = ["sshuttle", f"{subnet_options}", f"{extra_options}", "-r", f"{destination}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


@dataclasses.dataclass
class Connection:
    controller: juju.Controller
    connection_process: Optional[subprocess.Popen]


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
    _connections = {}

    def __new__(cls):
        if getattr(cls, "_manager") is None:
            cls._manager = super(ConnectManager, cls).__new__(cls)

        return cls._manager

    @property
    def connections(self) -> Dict[str, Connection]:
        """Return list of connections ."""
        return self._connections

    async def clean(self):
        """Close all connections."""
        for connection in self.connections.values():
            await connection.controller.disconnect()
            # if any connection process was used kill it
            if connection.connection_process:
                connection.connection_process.kill()

    async def get_controller(
        self, config: Dict[str, Any()], sshuttle: bool = False, reconnect: bool = False
    ) -> juju.Controller:
        """Get controller."""
        controller = self.connections.get(config["name"]).controller
        if controller is None:
            controller = await self.get_controller(config, sshuttle)
        elif reconnect:
            await controller.disconnect()
            controller = await self.get_controller(config, sshuttle)

        # TODO: add connection validation and reconnect if it's needed
        return controller

    # TODO: add controller_config typehint
    async def connect(self, controller_config, sshuttle: bool = False) -> juju.Controller:
        """Prepare connection to Controller and return it."""
        controller = juju.Controller()
        local_endpoint = None
        connection_process = None
        if controller_config.connection and not sshuttle:
            port = get_free_tcp_port()
            local_endpoint = f"localhost:{port}"
            connection_process = ssh_port_forwarding_proc(
                local_endpoint,
                controller_config.endpoint,
                controller_config.connection.destination,
                controller_config.connection.jumps,
            )
        elif controller_config.connection and sshuttle:
            connection_process = sshuttle_proc(
                controller_config.connection.destination,
                controller_config.connection.subnets,
                controller_config.connection.jumps,
            )

        await controller.connect(
            endpoint=local_endpoint or controller_config.endpoint,
            username=controller_config.username,
            password=controller_config.password,
            cacert=controller_config.ca_cert,
        )
        self.connections[controller_config.name] = Connection(controller, connection_process)
        return controller


get_controller = ConnectManager().get_controller
