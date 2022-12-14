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

"""Command entrypoint for ControllerInformationCommand."""
import textwrap

from multijuju.assignment.runner import run
from multijuju.async_handler import run_async
from multijuju.commands.show_controller import ShowControllerCommand

from .base import BaseCMD
from .fill import add_assignment_argument, add_connection_manager_argument


class ShowControllerInformationCMD(BaseCMD):
    """Show controller information."""

    name = "show-controller"
    help_msg = "Show controller information"
    overview = textwrap.dedent(
        """
        Show controller information
        """
    )

    def fill_parser(self, parser):
        """Add own parameters to the general parser."""
        add_connection_manager_argument(parser=parser)
        add_assignment_argument(parser=parser)
        parser.add_argument(
            "--yes",
            dest="yes or not",
            help="...",
        )

    def execute(self, parsed_args):
        return run_async(run(ShowControllerCommand(), parsed_args))
