"""Basic logic of showing controller information.

Provides different ways to run the Juju command:

    - Batch: 20 commands in 5 parallel
    - Parallel: 20 in parallel
    - Serial: 20 commands in 1 parallel
"""

from argparse import Namespace
from collections import defaultdict
from typing import Any, Dict

import juju
from juju.model import Model

from multijuju.commands.base import BaseJujuCommand, CommandTarget


async def get_controller():
    """Get controller for local controller.

    Dummy function used only for short term.
    """
    controller = juju.controller.Controller(max_frame_size=6**24)
    await controller.connect()
    return controller


async def run_parallel(command: BaseJujuCommand, parsed_args):
    pass


async def run_serial(command: BaseJujuCommand, parsed_args) -> Dict[str, Any]:
    """Run controller target command serially.

    Parameters:
        command(BaseJujuCommand): command to run
        parsed_args(Namespace): Namespace from CLI
    Returns:
        results(Dict): Controller dict with result.
    """
    results = {}
    for controller_config in parsed_args.filter.controllers:
        controller = await get_controller()

        output = await command.run(
            controller=controller,
            parsed_args=parsed_args,
        )
        results[controller_config.name] = output
    return results


async def run_batch(command: BaseJujuCommand, parsed_args):
    pass


async def run_parallel_model(command: BaseJujuCommand, parsed_args):
    pass


async def run_batch_model(command: BaseJujuCommand, parsed_args):
    pass


async def run_serial_model(command: BaseJujuCommand, parsed_args: Namespace) -> Dict[str, Dict[str, Any]]:
    """Run model target command serially.

    Parameters:
        command(BaseJujuCommand): command to run
        parsed_args(Namespace): Namespace from CLI
    Returns:
        results(Dict): Controller dict which value is model dict.
    """
    results: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(dict))
    for controller_config in parsed_args.filter.controllers:
        controller = await get_controller()
        model_names = await controller.get_models()

        for model_name in model_names:
            if (parsed_args.models and model_name in parsed_args.models) or not parsed_args.models:
                model = Model()
                await model.connect_model(model_name=model_name)
                output = await command.run(
                    controller=controller,
                    model=model,
                    parsed_args=parsed_args,
                )
                results[controller_config.name][model_name] = output
    return results


async def run(command: BaseJujuCommand, parsed_args):
    run_type = parsed_args.run_type
    if command.target() == CommandTarget.MODEL:
        if run_type == "parallel":
            return await run_parallel_model(command, parsed_args)
        if run_type == "batch":
            return await run_batch_model(command, parsed_args)
        return await run_serial_model(command, parsed_args)

    if command.target() == CommandTarget.CONTROLLER:
        if run_type == "parallel":
            return await run_parallel(command, parsed_args)
        if run_type == "batch":
            return await run_batch(command, parsed_args)
        return await run_serial(command, parsed_args)
