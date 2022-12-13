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

"""multijuju version command."""
import argparse
import textwrap

from craft_cli import BaseCommand, emit

from multijuju import settings


class VersionCMD(BaseCommand):
    """multijuju version command."""

    name = "version"
    help_msg = "Gets the status of selected model"
    overview = textwrap.dedent(
        """
    The status command shows the version of multijuju.

    Example:
    """
    )

    def fill_parser(self, parser: "argparse.ArgumentParser") -> None:
        pass

    def run(self, parsed_args):
        emit.message(settings.APP_VERSION)
