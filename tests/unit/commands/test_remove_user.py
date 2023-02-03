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
from unittest import mock

import pytest
from juju import juju

from juju_spell.commands.remove_user import RemoveUserCommand


@pytest.mark.asyncio
async def test_ping_execute():
    """Test execute function for RemoveUserCommand."""
    user = "test-user"
    controller = mock.MagicMock(spec=juju.Controller)

    remove_user = RemoveUserCommand()
    result = await remove_user.execute(controller, user=user)

    controller.remove_user.assert_called_once_with(username=user)
    assert result is True
