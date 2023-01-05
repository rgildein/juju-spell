from unittest.mock import AsyncMock

import pytest

from juju_spell.commands.show_controller import ShowControllerCommand


@pytest.mark.asyncio
async def test_execute():
    """Test execute function for ShowControllerCommand."""
    mock_controller = AsyncMock()
    show_controller = ShowControllerCommand()

    info = await show_controller.execute(controller=mock_controller)

    mock_controller.info.assert_awaited_once()
    assert info == mock_controller.info.return_value
