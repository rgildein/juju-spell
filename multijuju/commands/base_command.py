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
from abc import ABC

from craft_cli import emit
from juju.controller import Controller


class BaseJujuCommand(ABC):
    async def run(self, filtered_list, **kwargs):
        result_list = []
        for cloud in filtered_list:
            controller = await self.open_connection(cloud)
            result = await self.execute(controller, **kwargs)
            self.close_connection(controller)
            result_list.append(result)
        return result_list

    async def execute(self, controller: Controller, **kwargs):
        pass

    async def open_connection(self, cloud) -> Controller:
        emit.message("opening connection")
        controller = Controller()
        await controller.connect_controller(cloud)
        return controller

    async def close_connection(self, controller: Controller):
        controller.disconnect()
        emit.message("closing connection")
