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

"""JujuSpell juju ping command."""
import textwrap

from juju_spell.cli.base import JujuReadCMD
from juju_spell.commands.ping import PingCommand


class PingCMD(JujuReadCMD):
    """JujuSpell ping command to verify connection to controller."""

    name = "ping"
    help_msg = "Check connection to controller(s)"
    overview = textwrap.dedent(
        """
        The ping command check connection to controller(s).
    
        Example:
        $ juju-spell ping
        [
         {
          "context": {
           "uuid": "e9fe93a8-b705-4067-8f30-6eec183eeb4f",
           "name": "controller1",
           "customer": "Gandalf"
          },
          "success": true,
          "output": "accessible",
          "error": null
         }
        ]
        """
    )
    command = PingCommand
