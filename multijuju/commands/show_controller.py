"""Command entrypoint for ControllerInformationCommand."""
import textwrap

from craft_cli import BaseCommand, emit

from multijuju.async_handler import run_async
from multijuju.juju_commands.show_controller import cmd_show_controller


class ShowControllerInformationCommand(BaseCommand):
    """Show controller information."""

    name = "show-controller"
    help_msg = "Remove the indicated file."
    overview = textwrap.dedent(
        """
        Show controller information
        """
    )

    def fill_parser(self, parser):
        """Add own parameters to the general parser."""
        pass

    def run(self, parsed_args):
        emit.message("Start Command {}.".format("controller info"))
        run_async(_exec(parsed_args))
        emit.message("Command {} successfully.".format("controller info"))


async def _exec(
    parser_args,
):
    """Async function with business logic.

    This function should be refactored later if we have multiple similar work flow.
    """
    # Select/filter here
    # connection manager here
    emit.message(
        "Start command {} on cloud {}".format("controller-info", "{cloud name}")
    )
    await cmd_show_controller(
        controller_name="lxd-local",  # This need to be update later
    )
