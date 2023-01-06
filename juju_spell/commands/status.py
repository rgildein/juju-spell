from typing import Dict, List, Optional

from juju.client._definitions import FullStatus
from juju.controller import Controller

from juju_spell.commands.base import BaseJujuCommand


class StatusCommand(BaseJujuCommand):
    """Command to show status for models."""

    async def execute(
        self, controller: Controller, models: Optional[List[str]] = None, **kwargs
    ) -> Dict[str, FullStatus]:
        """Get status for selected models in controller."""
        output = {}
        async for name, model in self.get_filtered_models(controller, models):
            status = await model.get_status()
            output[name] = status

        return output
