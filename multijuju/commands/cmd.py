"""Module combinates all the commands."""
import sys

from craft_cli import (
    ArgumentParsingError,
    CommandGroup,
    CraftError,
    Dispatcher,
    EmitterMode,
    ProvideHelpException,
    emit,
)

from multijuju.settings import APP_NAME, VERSION

from .show_controller import ShowControllerInformationCommand


def exec_cmd():
    """Execute craft cli."""
    emit.init(
        EmitterMode.BRIEF,
        APP_NAME,
        f"Starting {APP_NAME} app {VERSION}.",
    )
    command_groups = [CommandGroup("Controller", [ShowControllerInformationCommand])]
    summary = "Execute command to multipule juju controllers."

    try:
        dispatcher = Dispatcher(
            APP_NAME,
            command_groups,
            summary=summary,
        )
        dispatcher.pre_parse_args(sys.argv[1:])
        dispatcher.load_command(None)
        dispatcher.run()
    except (ArgumentParsingError, ProvideHelpException) as err:
        print(err, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
    except CraftError as err:
        emit.error(err)
    except KeyboardInterrupt as exc:
        error = CraftError("Interrupted.")
        error.__cause__ = exc
        emit.error(error)
    except Exception as exc:
        error = CraftError(f"Application internal error: {exc!r}")
        error.__cause__ = exc
        emit.error(error)
    else:
        emit.ended_ok()
