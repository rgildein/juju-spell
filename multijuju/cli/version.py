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

"""Multijuju version command."""
import textwrap

from multijuju import settings
from multijuju.cli.base import BaseCMD


class VersionCMD(BaseCMD):
    """Get multijuju version command."""

    name = "version"
    help_msg = "Gets the version of multijuju."
    overview = textwrap.dedent(
        """
    The version command shows the version of multijuju.

    Example:

    $ multijuju version
    0.0.1
    """
    )

    def execute(self, parsed_args) -> str:
        """Return multijuju version."""
        return settings.APP_VERSION
