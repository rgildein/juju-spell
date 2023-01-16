"""Module combinates all the commands."""
import contextlib
import logging
import os
import sys

import confuse
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

from juju_spell import cli, utils
from juju_spell.config import load_config
from juju_spell.settings import APP_NAME, APP_VERSION, CONFIG_PATH, PERSONAL_CONFIG_PATH

COMMAND_GROUPS = [
    CommandGroup(
        "ReadOnly", [cli.StatusCMD, cli.ShowControllerInformationCMD, cli.PingCMD]
    ),
    CommandGroup("ReadWrite", [cli.AddUserCMD, cli.GrantCMD]),
    CommandGroup("Other", [cli.VersionCMD]),
]

GLOBAL_ARGS = [
    GlobalArgument(
        "version", "flag", "-v", "--version", "Show the application version and exit"
    ),
    GlobalArgument(
        "config", "option", "-c", "--config", "Set the path to custom config."
    ),
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
        if utils.strtobool(os.getenv("JUJUSPELL_ENABLE_DEVELOPER_DEBUG", "n").strip()):
            verbosity = EmitterMode.DEBUG

    # if defined, use environmental variable SNAPCRAFT_VERBOSITY_LEVEL
    verbosity_env = os.getenv("JUJUSPELL_VERBOSITY_LEVEL")
    if verbosity_env:
        try:
            verbosity = EmitterMode[verbosity_env.strip().upper()]
        except KeyError:
            values = utils.humanize_list(
                [e.name.lower() for e in EmitterMode], "and", sort=False
            )
            raise ArgumentParsingError(
                f"cannot parse verbosity level {verbosity_env!r} from environment "
                f"variable SNAPCRAFT_VERBOSITY_LEVEL (valid values are {values})"
            ) from KeyError

    return verbosity


def get_dispatcher() -> Dispatcher:
    """Return an instance of Dispatcher.

    Run all the checks and setup required to ensure the Dispatcher can run.
    """
    verbosity = get_verbosity()
    emit.init(verbosity, APP_NAME, f"Starting {APP_NAME} app {APP_VERSION}.")

    # configure logging
    logger = logging.getLogger()
    logger.setLevel(
        logging.DEBUG
    )  # set root logger to debug level so that all messages are sent to Emitter

    emit.debug(f"verbosity is set to {verbosity}")
    return Dispatcher(
        APP_NAME,
        COMMAND_GROUPS,
        summary="One juju to rule them all.",
        extra_global_args=GLOBAL_ARGS,
    )


def exec_cmd() -> int:
    """Execute craft cli."""
    dispatcher = get_dispatcher()
    return_code = 0

    try:
        global_args = dispatcher.pre_parse_args(sys.argv[1:])
        if global_args.get("config"):
            config = load_config(global_args["config"])
        else:
            config = load_config(CONFIG_PATH, PERSONAL_CONFIG_PATH)

        dispatcher.load_command(config)
        dispatcher.run()
    except ArgumentParsingError as error:
        print(error, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
        return_code = 127
    except ProvideHelpException as error:
        print(error, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
        return_code = 0
    except confuse.exceptions.ConfigError as error:
        print(
            f"error parsing configuration: `{error}`", file=sys.stderr
        )  # to stderr, as argparse normally does
        emit.ended_ok()
        return_code = 1
    except CraftError as err:
        emit.error(err)
        return_code = 1
    except KeyboardInterrupt as exc:
        error = CraftError("Interrupted.")
        error.__cause__ = exc
        emit.error(error)
        return_code = 130
    except Exception as exc:
        error = CraftError(f"Application internal error: {exc!r}")
        error.__cause__ = exc
        emit.error(error)
        return_code = 1

    return return_code
