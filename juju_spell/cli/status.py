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

"""JujuSpell juju status command."""
import textwrap

from craft_cli.dispatcher import _CustomArgumentParser

from juju_spell.cli.base import JujuReadCMD
from juju_spell.commands.status import StatusCommand


class StatusCMD(JujuReadCMD):
    """JujuSpell juju status command."""

    name = "status"
    help_msg = "Gets the status of selected model"
    overview = textwrap.dedent(
        """
        The status command shows the status of the selected model.

        Example:
        $ juju-spell status
        [
         {
          "context": {
           "uuid": "e9fe93a8-b705-4067-8f30-6eec183eeb4f",
           "name": "Controller1",
           "customer": "Gandalf"
          },
          "success": true,
          "output": {
           ...
           }
          },
          "error": null
         }
        ]
        """
    )
    command = StatusCommand

    def fill_parser(self, parser: _CustomArgumentParser) -> None:
        """Add arguments specific to the export-login command."""
        super().fill_parser(parser)
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
