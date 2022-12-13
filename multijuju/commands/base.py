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

"""multijuju base juju command."""
from abc import ABC, abstractmethod

from juju.controller import Controller


class BaseJujuCommand(ABC):
    async def run(self, controller: Controller, **kwargs):
        """Wrap only wrapper."""
        return await self.execute(controller, **kwargs)

    @staticmethod
    def need_sshuttle():
        return False

    @abstractmethod
    async def execute(self, controller: Controller, **kwargs):
        """Execute function.

        This part will be the main part function
        Args:
            controller: This will be juju controller
            kwargs: This will be the kwargs passed to the function which
                will contain the config for the selected controller
        """
        pass
