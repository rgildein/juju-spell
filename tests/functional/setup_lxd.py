# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""JujuSpell configuration for functional tests."""
import json
import random
import subprocess
import textwrap
from pathlib import Path
from string import ascii_lowercase
from time import sleep
from typing import Any, Dict, List, Tuple, Union

import yaml
from pylxd import Client
from pylxd.models import Container, Instance

from juju_spell.config import convert_config

CONTAINER_PREFIX = "JujuSpell"
DEFAULT_DIRECTORY = Path("/home/ubuntu/.local/share/juju-spell")
SSH_CONFIG = textwrap.dedent(
    """
Host *
  StrictHostKeyChecking=accept-new
"""
)
CONTROLLER_API_PORT = 17007
NUMBER_OF_CONTROLLERS = 2


def get_uuid(length: int) -> str:
    """Get random uuid."""
    return "".join(random.choice(ascii_lowercase) for _ in range(length))


def get_controller(name: str) -> Dict[str, Any]:
    """Get information about controller."""
    output = subprocess.check_output(
        ["juju", "show-controller", "--show-password", "--format", "json", name]
    ).decode()
    return json.loads(output)


def try_unregister_controller(name: str) -> None:
    """Try to unregister controller without raising error."""
    try:
        subprocess.check_call(
            ["juju", "unregister", "-y", name],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(f"Juju: controller {name} was unregistered")


def create_container(name: str, series: str) -> Container:
    """Create instance."""
    client = Client()
    container_name = f"{CONTAINER_PREFIX}-{name}-{get_uuid(5)}"
    config = {
        "name": container_name,
        "source": {
            "type": "image",
            "mode": "pull",
            "server": "https://cloud-images.ubuntu.com/daily",
            "protocol": "simplestreams",
            "alias": series,
        },
        "type": "container",
    }

    print(f"LXD: creating {name} with name: `{container_name}` and series {series}")
    container: Container = client.containers.create(config, wait=True)
    container.start(wait=True)
    print(f"LXD: {container.name} is running")
    return container


def create_client_instance(series: str, snap_path: Union[str, Path]) -> Instance:
    """Create client instance."""
    client = create_container("client", series)
    sleep(5)  # TODO: we need to wait for container to be fully readyx
    client.execute(["sudo", "ufw", "enable"], user=1000)
    # drop direct connection to any controller, e.g. <ip>:CONTROLLER_API_PORT
    client.execute(["sudo", "ufw", "deny", "out", str(CONTROLLER_API_PORT)], user=1000)
    client.execute(
        ["ssh-keygen", "-q", "-f", "/home/ubuntu/.ssh/id_rsa", "-N", ""], user=1000
    )
    with open(snap_path, "rb") as snap:
        client.files.put(
            "/home/ubuntu/juju-spell.snap", snap.read(), uid=1000, gid=1000
        )

    client.execute(
        ["sudo", "snap", "install", "./juju-spell.snap", "--devmode"],
        user=1000,
        cwd="/home/ubuntu",
    )

    # NOTE (rgildein): Right now JujuSpell is not creating `.local/share/juju-spell`
    # directory, so we need to create it
    client.execute(["mkdir", "-p", str(DEFAULT_DIRECTORY)], user=1000)

    return client


def boostrap_controller(name: str, series: str, ssh_key: str) -> Instance:
    """Bootstrap controller on top of instance."""
    # NOTE (rgildein): we could not use f"--config authorized-keys='{ssh_key}'",
    # because it's not appending key and Juju will not have access to this controller
    subprocess.check_output(
        [
            "juju",
            "bootstrap",
            "--no-switch",
            "--bootstrap-series",
            f"{series}",
            "--config",
            f"api-port={CONTROLLER_API_PORT}",
            "--config",
            f"default-series={series}",
            "localhost",
            name,
        ]
    )
    info = subprocess.check_output(
        ["juju", "show-controller", name.lower(), "--format", "json"]
    ).decode()
    info = json.loads(info)
    instance_id = info[name.lower()]["controller-machines"]["0"]["instance-id"]
    client = Client()
    # ranme controller container so we can easily access it a remove it later
    controller = client.instances.get(instance_id)
    controller.execute(
        ["sh", "-c", f"echo '{ssh_key}'>>/home/ubuntu/.ssh/authorized_keys"],
        user=1000,
    )
    controller.stop(wait=True)
    controller.rename(name, wait=True)
    controller.start(wait=True)
    return controller


def setup_environment(
    series: str, snap_path: Union[str, Path]
) -> Tuple[str, List[str]]:
    """Set up LXD environment.

    Creates client with JujuSpell installed and NUMBER_OF_CONTROLLERS for testing.
    """
    # JujuSpell client
    client = create_client_instance(series, snap_path)  # JujuSpell client
    client_ssh_key = client.execute(
        ["cat", "/home/ubuntu/.ssh/id_rsa.pub"], user=1000
    ).stdout.strip()
    # Note(rgildein): Right now our connection could not accept ssh key
    # automaticaly, that's why we need to do this
    client.files.put("/home/ubuntu/.ssh/config", SSH_CONFIG, uid=1000)

    # controllers
    controllers = []
    for _ in range(NUMBER_OF_CONTROLLERS):
        name = f"{CONTAINER_PREFIX}-controller-{get_uuid(5)}"
        controller = boostrap_controller(name, series, client_ssh_key)
        controllers.append(controller.name)

    # creates JujuSpell config
    config = {"controllers": []}
    for controller in controllers:
        info = convert_config(get_controller(controller.lower()))
        ip_address, _ = info["endpoint"].split(":")
        config["controllers"].append(
            {
                "owner": "Frodo",
                "customer": "Gandalf",
                **info,
                "connection": {"destination": ip_address},
            }
        )
    config_string = yaml.safe_dump(config)
    client.files.put(
        DEFAULT_DIRECTORY / "config.yaml", config_string, uid=1000, gid=1000
    )

    return client.name, controllers


def cleanup_environment():
    """Clean up LXD environment.

    Remove all instances with names starting with CONTAINER_PREFIX.
    """
    client = Client()
    for instance in client.instances.all():
        if instance.name.startswith(CONTAINER_PREFIX):
            if instance.status_code != 102:  # check if instance is not already stopped
                instance.stop(wait=True)

            instance.delete()
            print(f"LXD: {instance.name} was removed")
            try_unregister_controller(instance.name.lower())
