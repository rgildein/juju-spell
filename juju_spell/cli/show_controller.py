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

from juju_spell.cli.base import JujuReadCMD
from juju_spell.commands.show_controller import ShowControllerCommand


class ShowControllerInformationCMD(JujuReadCMD):
    """Show controller information."""

    name = "show-controller"
    help_msg = "Show controller information"
    overview = textwrap.dedent(
        """
        Show controller information

        Example:
        $ juju-spell show-controller
        [
         {
          "context": {
           "uuid": "e9fe93a8-b705-4067-8f30-6eec183eeb4f",
           "name": "controller1",
           "customer": "Gandalf"
          },
          "success": true,
          "output": {
           "results": [
            {
             "addresses": [
              "1.2.3.4:17070"
             ],
             "cacert": "...",
             "error": null,
             "unknown_fields": {}
            }
           ],
           "unknown_fields": {}
          },
          "error": null
         }
        ]
        """
    )
    command = ShowControllerCommand
