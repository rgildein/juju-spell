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

"""JujuSpell base juju command."""
import logging
from abc import ABCMeta, abstractmethod
from typing import Any, AsyncGenerator, List, Optional, Tuple

from juju.controller import Controller
from juju.model import Model


class BaseJujuCommand(metaclass=ABCMeta):
    """Base Juju commands."""

    def __init__(self):
        """Init for command."""
        self.name = getattr(self.__class__, "__name__", "unknown")
        # TODO: we need to set logging formatter for craft_cli
        # with format: "%(name)s: %(message)s"
        self.logger = logging.getLogger(self.name)

    @staticmethod
    async def get_filtered_models(
        controller: Controller, models: Optional[List[str]] = None
    ) -> AsyncGenerator[Tuple[str, Model], None]:
        """Get filtered models for controller.

        If models is None, then all models for controller will be returned.
        """
        all_models = await controller.get_models()
        for model_name in all_models:
            if not models or model_name in models:
                model = await controller.get_model(model_name)
                yield model_name, model
                await model.disconnect()

    async def run(self, controller: Controller, **kwargs):
        """Execute Juju command.

        **This function should not be changed.**
        """
        self.logger.info("%s running %s command", controller.controller_uuid, self.name)
        return await self.execute(controller, **kwargs)

    @property
    def need_sshuttle(self) -> bool:
        """Check if sshuttle is needed."""
        return False

    @abstractmethod
    async def execute(self, controller: Controller, **kwargs) -> Any:
        """Execute function.

        This part will be the main part function
        Args:
            controller: This will be juju controller
            kwargs: This will be the kwargs passed to the function which
                will contain the config for the selected controller
        """
        pass
