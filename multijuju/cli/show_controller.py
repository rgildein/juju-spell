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

from craft_cli import emit

from multijuju.async_handler import run_async
from multijuju.cli.base_cli import BaseCLICommand
from multijuju.commands.show_controller import cmd_show_controller


class ShowControllerInformationCommand(BaseCLICommand):
    """Show controller information."""

    name = "show-controller"
    help_msg = "Remove the indicated file."
    overview = textwrap.dedent(
        """
        Show controller information
        """
    )

    def fill_parser(self, parser):
        """Add own parameters to the general parser."""
        pass

    def execute(self, parsed_args):
        emit.message("Start Command {}.".format("controller info"))
        run_async(self._exec(parsed_args))
        emit.message("Command {} successfully.".format("controller info"))

    async def _exec(self, parser_args):
        """Async function with business logic."""
        emit.message("Start command {} on cloud {}".format("controller-info", "{cloud name}"))
        await cmd_show_controller(
            controller_name="overlord",  # This need to be update later
        )
