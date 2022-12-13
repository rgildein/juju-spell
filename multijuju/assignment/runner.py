"""Basic logic of showing controller information."""
import juju

from multijuju.commands.base import BaseJujuCommand


async def get_controller():
    """Get controller for local controller.

    Dummy function used only for short term.
    """
    controller = juju.controller.Controller(max_frame_size=6**24)
    await controller.connect()
    return controller


async def run_parallel(command: BaseJujuCommand, parsed_args):
    pass


async def run_serial(command: BaseJujuCommand, parsed_args):
    list = []
    # cm = ConnectManager()
    for controller_config in parsed_args.filtered_config.controllers:
        controller = await get_controller()
        output = await command.run(
            controller=controller,
            parsed_args=parsed_args,
        )
        list.append(output)
    return list


async def run_batch(command: BaseJujuCommand, parsed_args):
    pass


async def run(command: BaseJujuCommand, parsed_args):
    run_type = parsed_args.run_type
    if run_type == "parallel":
        return await run_parallel(command, parsed_args)
    elif run_type == "batch":
        return await run_batch(command, parsed_args)
    else:
        return await run_serial(command, parsed_args)
