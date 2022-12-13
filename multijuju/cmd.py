"""Module combinates all the commands."""
import argparse
import contextlib
import os
import sys

from craft_cli import (
    ArgumentParsingError,
    CommandGroup,
    CraftError,
    Dispatcher,
    EmitterMode,
    GlobalArgument,
    ProvideHelpException,
    emit,
)

from multijuju import cli, utils
from multijuju.settings import APP_NAME, APP_VERSION

COMMAND_GROUPS = [
    CommandGroup(
        "ReadOnly",
        [cli.JujuStatusCMD, cli.ShowControllerInformationCMD],
    ),
    CommandGroup(
        "ReadWrite",
        [
            cli.JujuActionsCLI,
        ],
    ),
    CommandGroup("Other", [cli.VersionCLI]),
]

GLOBAL_ARGS = [
    GlobalArgument("version", "flag", "-V", "--version", "Show the application version and exit"),
    GlobalArgument("trace", "flag", "-t", "--trace", argparse.SUPPRESS),
]


def get_verbosity() -> EmitterMode:
    """Return the verbosity level to use.

    if SNAPCRAFT_ENABLE_DEVELOPER_DEBUG is set, the
    default verbosity will be set to EmitterMode.DEBUG.
    If stdin is closed, the default verbosity will be
    set to EmitterMode.VERBOSE.
    """
    verbosity = EmitterMode.BRIEF

    if not sys.stdin.isatty():
        verbosity = EmitterMode.VERBOSE

    with contextlib.suppress(ValueError):
        # Parse environment variable for backwards compatibility with launchpad
        if utils.strtobool(os.getenv("MULTIJUJU_ENABLE_DEVELOPER_DEBUG", "n").strip()):
            verbosity = EmitterMode.DEBUG

    # if defined, use environmental variable SNAPCRAFT_VERBOSITY_LEVEL
    verbosity_env = os.getenv("MULTIJUJU_VERBOSITY_LEVEL")
    if verbosity_env:
        try:
            verbosity = EmitterMode[verbosity_env.strip().upper()]
        except KeyError:
            values = utils.humanize_list([e.name.lower() for e in EmitterMode], "and", sort=False)
            raise ArgumentParsingError(
                f"cannot parse verbosity level {verbosity_env!r} from environment "
                f"variable SNAPCRAFT_VERBOSITY_LEVEL (valid values are {values})"
            ) from KeyError

    return verbosity


def exec_cmd():
    """Execute craft cli."""
    emit.init(
        get_verbosity(),
        APP_NAME,
        f"Starting {APP_NAME} app {APP_VERSION}.",
    )
    summary = "One juju to rule them all."

    try:
        dispatcher = Dispatcher(
            APP_NAME,
            COMMAND_GROUPS,
            summary=summary,
            extra_global_args=GLOBAL_ARGS,
            default_command=cli.VersionCLI,
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
