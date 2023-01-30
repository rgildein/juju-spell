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
"""JujuSpell juju remove user command."""
import textwrap

from craft_cli.dispatcher import _CustomArgumentParser

from juju_spell.cli.base import JujuWriteCMD
from juju_spell.commands.remove_user import RemoveUserCommand


class RemoveUserCMD(JujuWriteCMD):
    """JujuSpell remove user command."""

    name = "remove-user"
    help_msg = "remove juju user to remote controller"
    overview = textwrap.dedent(
        """
        The command will remove user on controller.

        Example:
        $ juju_spell remove-user --user newuser

        [
          [
            {
              "context": {
                "name": "controller1",
                "customer": "customer1"
              },
              "output": null
            },
            {
              "context": {
                "name": "controller2",
                "customer": "customer2"
              },
              "output": null
            }
          ]
        ]
        """
    )

    command = RemoveUserCommand

    def fill_parser(self, parser: _CustomArgumentParser) -> None:
        super().fill_parser(parser=parser)
        parser.add_argument(
            "--user",
            type=str,
            help="username to remove",
            required=True,
        )
