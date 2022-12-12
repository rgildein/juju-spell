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
import textwrap

from multijuju.assignment.runner import run
from multijuju.async_handler import run_async
from multijuju.cli.base import BaseCLICommand
from multijuju.commands.juju_status_command import JujuStatusCommand

from .fill import add_assignment_argument, add_connection_manager_argument


class JujuStatusCMD(BaseCLICommand):
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
        add_assignment_argument(parser)
        add_connection_manager_argument(parser)
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
        run_async(run(JujuStatusCommand(), parsed_args))
