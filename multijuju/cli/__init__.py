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

"""Multijuju cli commands."""
from craft_cli import CommandGroup

from .show_controller import ShowControllerInformationCMD
from .status import StatusCMD
from .version import VersionCMD

COMMAND_GROUPS = [
    CommandGroup("ReadOnly", [StatusCMD, ShowControllerInformationCMD]),
    # CommandGroup("ReadWrite", []),
    CommandGroup("Other", [VersionCMD]),
]
__all__ = ["COMMAND_GROUPS", "StatusCMD", "VersionCMD", "ShowControllerInformationCMD"]
