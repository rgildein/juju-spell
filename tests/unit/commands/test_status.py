from typing import AsyncGenerator, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from juju_spell.commands.status import StatusCommand


async def _async_generator(values: List) -> AsyncGenerator:
    """Async generator."""
    for value in values:
        yield value


@pytest.mark.asyncio
@patch("juju_spell.commands.base.BaseJujuCommand.get_filtered_models")
async def test_execute(mocked_models):
    """Test execute function for StatusCommand."""
    models = [("model1", AsyncMock()), ("model2", AsyncMock())]
    mocked_models.return_value = _async_generator(models)
    status = StatusCommand()

    results = await status.execute(MagicMock())

    assert len(results) == len(models)
    for name, model in models:
        assert results[name] == model.get_status.return_value
        model.get_status.assert_awaited_once()
