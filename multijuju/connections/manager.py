import dataclasses
import socket
import subprocess
from typing import Dict, List, Optional

from juju import juju

from multijuju.config import Controller

MAX_FRAME_SIZE = 6**24


def get_free_tcp_port() -> int:
    """Get free TCP port.

    This function will return free port on local system. This port will be used to port-forward remote controller
    to localhost:<port>.
    """
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    # TODO: we need to select a port from the predefined range
    _, port = tcp.getsockname()
    tcp.close()
    return port


def ssh_port_forwarding_proc(
    local_target: str, remote_target: str, destination: str, jumps: Optional[List[str]] = None
) -> subprocess.Popen:
    """Port forward target through destination.

    Example:
    Call this function as follows
    ```python
    ssh_port_forwarding_proc("localhost:17071", "10.1.1.99:17070", "gandalf@customer", ["bastion"])
    ```
    is equivalent to
    ```bash
    ssh -N -L localhost:17071:10.1.1.99:17070 -J bastion gandalf@customer
    ```
    and it will port-forward the `10.1.1.99:17070` to `localhost:17071`.

    :param local_target: bind_address:port to which remote target will be port-forwarded
    :param remote_target: remote host and port, which will be port-forwarded
    :param destination: ssh destination, which may be specified as either [user@]hostname or a URI of the form
                        `ssh://[user@]hostname[:port]`
    :param jumps: connect to the destination by first making a ssh connection via list of jumps host described by
                  destination
    """
    jumps = jumps or []
    jumps_option = " ".join(f"-J {jump}" for jump in jumps)

    cmd = ["ssh", "-N", "-L", f"{local_target}:{remote_target}", jumps_option, destination]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def sshuttle_proc(subnets: List[str], destination: str, jumps: Optional[List[str]] = None) -> subprocess.Popen:
    """Create sshuttle tunnel.

    Example:
    Call this function as follows
    ```python
    sshuttle_proc(["10.1.1.0/24"], "gandalf@customer", ["bastion"])
    ```
    is equivalent to
    ```bash
    sshuttle -r gandalf@customer -e 'ssh -J bastion' 10.1.1.0/24
    ```
    and it will create ssh tunnel and add subnetworks to iptables. This will redirect all traffic to subnets through
    this tunnel.

    :param subnets: capture and forward traffic to these subnets
    :param destination: ssh hostname (and optional username and password) of remote sshuttle server
                        [USERNAME[:PASSWORD]@]ADDR[:PORT]
    :param jumps: connect to the destination by first making a ssh connection via list of jumps host described by
                  destination
    """
    jumps = jumps or []
    jumps_option = " ".join(f"-J {jump}" for jump in jumps)
    extra_options = "" if not jumps else f"-e 'ssh {jumps_option}'"

    cmd = ["sshuttle", "-r", destination, extra_options, *subnets]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


@dataclasses.dataclass
class Connection:
    controller: juju.Controller
    connection_process: Optional[subprocess.Popen]


class ConnectManager(object):
    """Connect manager is used to define connections for controllers.

    Usage
        example 1

        ```python
        async def task(...):
            ...
            connect_manager = ConnectManager():
            controller = await connect_manager.get_controller(controller_config)
            ...
        ```

        example 2

        ```python
        from multijuju.connection import connect_manager

        async def task1(...):
            ...
            controller = await connect_manager.get_controller(controller_config)
            ...

        async def task2(...):
            ...
            # return same controller
            controller = await connect_manager.get_controller(controller_config)
            ...
        ```
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

    async def _connect(self, controller_config: Controller, sshuttle: bool = False) -> juju.Controller:
        """Prepare connection to Controller and return it."""
        controller = juju.Controller(max_frame_size=MAX_FRAME_SIZE)
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
                controller_config.connection.subnets,
                controller_config.connection.destination,
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

    async def clean(self):
        """Close all connections."""
        controllers = self.connections.copy().keys()  # get keys from copy
        for name in controllers:
            connection = self.connections[name]
            await connection.controller.disconnect()
            # if any connection process was used kill it
            if connection.connection_process:
                connection.connection_process.terminate()

            del self.connections[name]

    async def get_controller(
        self, controller_config: Controller, sshuttle: bool = False, reconnect: bool = False
    ) -> juju.Controller:
        """Get controller."""
        assert isinstance(controller_config, Controller), "Not supported format of controller config"

        connection = self.connections.get(controller_config.name)
        if connection and connection.controller.is_connected() and not reconnect:
            return connection.controller
        elif connection and reconnect:
            await connection.controller.disconnect()

        return await self._connect(controller_config, sshuttle)
