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
from typing import Optional

from juju.controller import Controller
from juju.errors import JujuError

from juju_spell.commands.base import BaseJujuCommand

__all__ = ["RemoveUserCommand"]


class RemoveUserCommand(BaseJujuCommand):
    async def execute(
        self, controller: Controller, *, user: Optional[str] = None, **kwargs
    ) -> str:
        try:
            await controller.remove_user(username=user)
            return f"user `{user}` was successfully removed"
        except JujuError as error:
            self.logger.exception(error)
            return f"failed to delete user `{user}` with error: {error}"
