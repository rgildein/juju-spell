# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Command-line application entry point."""

import argparse
import contextlib
import sys

import craft_cli
from craft_cli import ArgumentParsingError, EmitterMode, ProvideHelpException, emit

from multijuju import cli

COMMAND_GROUPS = [
    craft_cli.CommandGroup(
        "ReadOnly",
        [
            cli.JujuStatusCLI,
        ],
    ),
    craft_cli.CommandGroup(
        "ReadWrite",
        [
            cli.JujuActionsCLI,
        ],
    ),
    craft_cli.CommandGroup("Other", [cli.VersionCLI]),
]

GLOBAL_ARGS = [
    craft_cli.GlobalArgument("version", "flag", "-V", "--version", "Show the application version and exit"),
    craft_cli.GlobalArgument("trace", "flag", "-t", "--trace", argparse.SUPPRESS),
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
        verbosity = EmitterMode.DEBUG

    return verbosity


def get_dispatcher() -> craft_cli.Dispatcher:
    """Return an instance of Dispatcher.

    Run all the checks and setup required to ensure the Dispatcher can run.
    """
    emit.init(mode=get_verbosity(), appname="multijuju", greeting="Starting multijuju 0.0.1")

    return craft_cli.Dispatcher(
        "multijuju",
        COMMAND_GROUPS,
        summary="One juju to rule them all",
        extra_global_args=GLOBAL_ARGS,
        default_command=cli.VersionCLI,
    )


def _run_dispatcher(dispatcher: craft_cli.Dispatcher) -> None:
    dispatcher.pre_parse_args(sys.argv[1:])
    # if global_args.get("version"):
    #     emit.message(f"snapcraft {__version__}")
    # else:
    #     if global_args.get("trace"):
    #         emit.message(
    #             "Options -t and --trace are deprecated, use --verbosity=debug instead."
    #         )
    #         emit.set_mode(EmitterMode.DEBUG)

    dispatcher.load_command(None)
    dispatcher.run()
    emit.ended_ok()


def _emit_error(error, cause=None):
    """Emit the error in a centralized way so we can alter it consistently."""
    # set the cause, if any
    if cause is not None:
        error.__cause__ = cause

    emit.error(error)


def run():  # noqa: C901
    """Run the CLI."""
    dispatcher = get_dispatcher()
    try:
        _run_dispatcher(dispatcher)
        retcode = 0
    except ArgumentParsingError as err:
        print(err, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
        retcode = 1
    except ProvideHelpException as err:
        print(err, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
        retcode = 0

    except KeyboardInterrupt as err:
        _emit_error(craft_cli.errors.CraftError("Interrupted."), cause=err)
        retcode = 1

    return retcode
