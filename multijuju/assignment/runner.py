"""Basic logic of showing controller information.

Provides different ways to run the Juju command:

    - Batch: 20 commands in 5 parallel
    - Parallel: 20 in parallel
    - Serial: 20 commands in 1 parallel
"""

from argparse import Namespace
from typing import Any, Dict, List

from juju.model import Model

from multijuju.commands.base import BaseJujuCommand, CommandTarget
from multijuju.config import Controller
from multijuju.connections import get_controller

REULT_TYPE = Dict[str, Dict[str, Any]]
RESULTS_TYPE = List[REULT_TYPE]


def get_result(controller_config: Controller, output: Any) -> REULT_TYPE:
    """Get command result."""
    return {
        "context": {
            "name": controller_config.name,
            "customer": controller_config.customer,
        },
        "output": output,
    }


async def run_parallel(command: BaseJujuCommand, parsed_args):
    pass


async def run_serial(command: BaseJujuCommand, parsed_args) -> RESULTS_TYPE:
    """Run controller target command serially.

    Parameters:
        command(BaseJujuCommand): command to run
        parsed_args(Namespace): Namespace from CLI
    Returns:
        results(Dict): Controller dict with result.
    """
    results: RESULTS_TYPE = []
    for controller_config in parsed_args.filter.controllers:
        controller = await get_controller(controller_config)

        output = await command.run(
            controller=controller,
            parsed_args=parsed_args,
        )
        results.append(get_result(controller_config, output))

    return results


async def run_batch(command: BaseJujuCommand, parsed_args):
    pass


async def run_parallel_model(command: BaseJujuCommand, parsed_args):
    pass


async def run_batch_model(command: BaseJujuCommand, parsed_args):
    pass


async def run_serial_model(command: BaseJujuCommand, parsed_args: Namespace) -> RESULTS_TYPE:
    """Run model target command serially.

    Parameters:
        command(BaseJujuCommand): command to run
        parsed_args(Namespace): Namespace from CLI
    Returns:
        results(Dict): Controller dict which value is model dict.
    """
    results: RESULTS_TYPE = []
    for controller_config in parsed_args.filter.controllers:
        controller = await get_controller(controller_config)
        model_names = await controller.get_models()
        outputs = {}

        for model_name in model_names:
            if not parsed_args.models or model_name in parsed_args.models:
                model = Model()
                await model.connect_model(model_name=model_name)
                output = await command.run(
                    controller=controller,
                    model=model,
                    parsed_args=parsed_args,
                )
                outputs[model_name] = output

        results.append(get_result(controller_config, outputs))

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
