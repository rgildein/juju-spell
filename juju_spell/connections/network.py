import logging
import random
import socket
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)


def _is_port_free(port: int) -> bool:
    """Check if port is free to use."""
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = tcp.connect_ex(("localhost", port))
    tcp.close()
    return result != 0


def get_free_tcp_port(port_range: range) -> int:
    """Get free TCP port from range.

    This function will return free port on local system. This port will be used to
    port-forward remote controller to localhost:<port>.
    """
    list_of_ports = list(port_range)
    random.shuffle(list_of_ports)  # randomly shuffle list of ports

    for port in list_of_ports:
        if _is_port_free(port):
            logger.debug("free port %d was found", port)
            return port

    raise ValueError(f"Could not find a free port in range {port_range}")


def ssh_port_forwarding_proc(
    local_target: str,
    remote_target: str,
    destination: str,
    jumps: Optional[List[str]] = None,
) -> subprocess.Popen:
    """Port forward target through destination.

    Example:
    Call this function as follows
    ```python
    ssh_port_forwarding_proc(
        "localhost:17071", "10.1.1.99:17070", "gandalf@customer", ["bastion"]
    )
    ```
    is equivalent to
    ```bash
    ssh -N -L localhost:17071:10.1.1.99:17070 -J bastion gandalf@customer
    ```
    and it will port-forward the `10.1.1.99:17070` to `localhost:17071`.

    :param local_target: bind_address:port to which remote target will be port-forwarded
    :param remote_target: remote host and port, which will be port-forwarded
    :param destination: ssh destination, which may be specified as either
                        [user@]hostname or a URI of the form
                        `ssh://[user@]hostname[:port]`
    :param jumps: connect to the destination by first making a ssh connection via list
                  of jumps host described by destination
    """
    logger.info(
        "port forwarding %s to %s via %s", remote_target, local_target, destination
    )
    jumps = jumps or []
    jumps_option = " ".join(f"-J {jump}" for jump in jumps)

    cmd = [
        "ssh",
        "-N",
        "-L",
        f"{local_target}:{remote_target}",
        jumps_option,
        destination,
    ]
    logger.debug("cmd `%s` will be executed", cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def sshuttle_proc(
    subnets: List[str], destination: str, jumps: Optional[List[str]] = None
) -> subprocess.Popen:
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
    and it will create ssh tunnel and add subnetworks to iptables. This will redirect
    all traffic to subnets through this tunnel.

    :param subnets: capture and forward traffic to these subnets
    :param destination: ssh hostname (and optional username and password) of remote
                        sshuttle server [USERNAME[:PASSWORD]@]ADDR[:PORT]
    :param jumps: connect to the destination by first making a ssh connection via list
                  of jumps host described by destination
    """
    logger.info("sshuttle %s subnets via %s", subnets, destination)
    jumps = jumps or []
    jumps_option = " ".join(f"-J {jump}" for jump in jumps)
    extra_options = "" if not jumps else f"-e 'ssh {jumps_option}'"

    cmd = ["sshuttle", "-r", destination, extra_options, *subnets]
    logger.debug("cmd `%s` will be executed", cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc
