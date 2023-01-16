from unittest.mock import AsyncMock

import pytest
from juju.controller import Controller

from juju_spell.commands.ping import PingCommand


def _get_mocked_controller(connected: bool) -> AsyncMock:
    """Get mocked Controller as MagicMock."""
    controller = AsyncMock(spec=Controller)
    controller.is_connected.return_value = connected
    return controller


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "controller, exp_result",
    [
        (_get_mocked_controller(True), "accessible"),
        (_get_mocked_controller(False), "unreachable"),
    ],
)
async def test_ping_execute(controller, exp_result):
    """Test execute function for PingCommand."""
    ping = PingCommand()
    result = await ping.execute(controller)
    assert result == exp_result
