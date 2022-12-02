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

"""multijuju juju actions command."""

import argparse
import textwrap

from craft_cli import emit

from multijuju.cli.base_cli import BaseCLICommand


class JujuActionsCLI(BaseCLICommand):
    """multijuju juju actions command."""

    name = "actions"
    help_msg = "Shows the actions of selected application"
    overview = textwrap.dedent(
        """
    The actions command shows the actions of the selected application.

    Example:
    """
    )

    def fill_parser(self, parser: "argparse.ArgumentParser") -> None:
        """Add arguments specific to the export-login command."""
        parser.add_argument(
            "application",
            default=str,
            help="Name of the application",
        )

    def execute(self, parsed_args):
        message = ""
        if parsed_args.application:
            message += f"${parsed_args.application} actions are restart, represent, click \n"
        emit.message(message)
