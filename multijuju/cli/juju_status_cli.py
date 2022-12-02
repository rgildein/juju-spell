# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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

"""multijuju juju status command."""
import argparse
import asyncio
import textwrap

from craft_cli import emit

from multijuju.cli.base_cli import BaseCLICommand
from multijuju.commands.juju_status_command import JujuStatusCommand


class JujuStatusCLI(BaseCLICommand):
    """multijuju juju status command."""

    name = "status"
    help_msg = "Gets the status of selected model"
    overview = textwrap.dedent(
        """
    The status command shows the status of the selected model.

    Example:
    """
    )

    def fill_parser(self, parser: "argparse.ArgumentParser") -> None:
        """Add arguments specific to the export-login command."""
        parser.add_argument(
            "--relations",
            default=False,
            help="Show 'relations' section",
        )
        parser.add_argument(
            "--storage",
            action="store_true",
            default=False,
            help="Show 'storage' section",
        )

    def execute(self, parsed_args):
        message = "running juju status with "
        if parsed_args.relations:
            message += "relations option added \n"

        if parsed_args.storage:
            message += "storage option added \n"

        juju_status_command = JujuStatusCommand()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(juju_status_command.run(["overlord"]))
        emit.message(message)


async def async_func(command):
    print("heelo")
    await command
    print("heelo333")
