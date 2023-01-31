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
import logging
import os
import subprocess
from pathlib import Path
from typing import Callable, Generator

import pylxd.models
import pytest
from pylxd import Client

from tests.functional.setup_lxd import cleanup_environment, setup_environment

logger = logging.getLogger(__name__)


DEFAULT_SERIES = "jammy"
CLIENT_CONAINER = pytest.StashKey[str]()
CONTROLLERS_CONTAINERS = pytest.StashKey[list]()


def check_dependencies(*dependencies) -> None:
    """Check if dependencies are installed."""
    errors = []
    for dependence in dependencies:
        try:
            subprocess.check_output(["which", dependence])
        except subprocess.CalledProcessError:
            errors.append(f"Missing {dependence} dependency.")

    if errors:
        raise RuntimeError(os.linesep.join(errors))


def build_snap(build: bool) -> Path:
    """Build JujuSpell snap."""
    path = Path("juju-spell.snap")
    if build:
        print("snapcraft: building JujuSpell")
        subprocess.check_output(["snapcraft", "pack"])
        subprocess.check_output(["bash", "rename.sh"])

    if path.exists():
        return path

    raise RuntimeError("Something went wrong with building snap")


def pytest_addoption(parser):
    """Add custom CLI options."""
    parser.addoption(
        "--series",
        type=str,
        default=DEFAULT_SERIES,
        help="create lxd controllers with series",
    )
    parser.addoption(
        "--no-build", action="store_false", help="flag to disable building new snap"
    )


def pytest_configure(config):
    """Configure environment."""
    series = config.getoption("series")
    build = config.getoption("no_build")

    check_dependencies("juju", "lxd", "snapcraft")
    snap_path = build_snap(build)
    try:
        client, controllers = setup_environment(series, snap_path)
        config.stash[CLIENT_CONAINER] = client
        config.stash[CONTROLLERS_CONTAINERS] = controllers
        config.add_cleanup(cleanup_environment)
    except Exception:
        cleanup_environment()
        raise


@pytest.fixture
def client(pytestconfig, tmp_path, controllers) -> pylxd.models.Instance:
    """Return LXD container where JujuSpell is installed."""
    name = pytestconfig.stash[CLIENT_CONAINER]
    client = Client()
    return client.instances.get(name)


@pytest.fixture
def controllers(pytestconfig) -> Generator[pylxd.models.Instance, None, None]:
    """Return LXD containers for controllers."""
    controllers = pytestconfig.stash[CONTROLLERS_CONTAINERS]
    client = Client()

    return (client.instances.get(name) for name in controllers)


@pytest.fixture
def juju_spell_run(client) -> Callable:
    """Return Callable function to execute JujuSpell command."""

    def wrapper(*args):
        return client.execute(
            ["juju-spell", *args], user=1000, group=1000, cwd="/home/ubuntu"
        )

    return wrapper
