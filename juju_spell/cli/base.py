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

"""JujuSpell base cli command."""
import argparse
import asyncio
import copy
import json
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Optional

from craft_cli import BaseCommand, emit
from craft_cli.dispatcher import _CustomArgumentParser

from juju_spell.assignment.runner import run
from juju_spell.cli.utils import confirm, parse_comma_separated_str, parse_filter
from juju_spell.commands.base import BaseJujuCommand
from juju_spell.settings import CONFIG_PATH


class BaseCMD(BaseCommand, metaclass=ABCMeta):
    """Base CLI command for handling contexts."""

    def __init__(self, *args, **kwargs) -> None:
        """Update initialization."""
        self.emit = emit
        super().__init__(*args, **kwargs)

    def fill_parser(self, parser: _CustomArgumentParser) -> None:
        """Define base arguments for commands."""
        parser.add_argument(
            "--config",
            type=Path,
            default=CONFIG_PATH,
            help="config file path",
        )
        parser.add_argument(
            "--silent",
            default=False,
            action="store_true",
            help="This will skip all the confirm check.",
        )

    def run(self, parsed_args: argparse.Namespace) -> Optional[int]:
        """Execute CLI command.

        **This function should not be changed.**
        """
        try:
            self.before(parsed_args)
            retval = self.execute(parsed_args)
            message = self.format_output(retval)
            self.emit.message(message)
            self.after(parsed_args)
            return 0
        except Exception as error:
            # TODO: improve exception handling
            self.emit.error(error)
            return 1

    def format_output(self, retval: Any) -> str:
        """Pretty formatter for output."""
        self.emit.debug(f"formatting the `{retval}` value")
        # TODO: support more types here
        if isinstance(retval, (dict, list)):
            # TODO: add support for table, yaml, ... format
            return json.dumps(retval, default=vars, indent=1)

        return str(retval)

    @abstractmethod
    def execute(self, parsed_args: argparse.Namespace) -> Any:
        """Abstract function need to be defined for each JujuSpell CLI command."""
        pass

    def before(self, parsed_args: argparse.Namespace) -> None:
        """Run before execution."""
        pass

    def after(self, parsed_args: argparse.Namespace) -> None:
        """Run after execution."""
        pass


class BaseJujuCMD(BaseCMD, metaclass=ABCMeta):
    """Base CLI command for handling any Juju commands."""

    @property
    @abstractmethod
    def command(self):
        pass

    def fill_parser(self, parser: _CustomArgumentParser) -> None:
        """Define base arguments for Juju commands.

        This will add arguments for connection, filtering and config.
        """
        super().fill_parser(parser)
        parser.add_argument(
            "--run-type",
            type=str,
            choices=["parallel", "batch", "serial"],
            default="serial",
            help="parallel, batch or serial",
        )
        parser.add_argument(
            "--filter",
            type=parse_filter,
            required=False,
            default="",
            help="""Key-value pair comma separated string in double quotes e.g., "a=1,2,3 b=4,5,6". """,
        )
        parser.add_argument(
            "--models",
            type=parse_comma_separated_str,
            help="model filter",
        )

    def execute(self, parsed_args: argparse.Namespace) -> Any:
        """Execute Juju Commands."""
        if self.command is None or not issubclass(self.command, BaseJujuCommand):
            raise RuntimeError(f"command `{self.command}` is incorrect")

        loop = asyncio.get_event_loop()  # TODO: optionally new event loop, it's needed ???
        task = loop.create_task(run(self.command(), parsed_args))
        return loop.run_until_complete(asyncio.gather(task))


class JujuReadCMD(BaseJujuCMD, metaclass=ABCMeta):
    """Base CLI command for handling Juju commands with read access."""


class JujuWriteCMD(BaseJujuCMD, metaclass=ABCMeta):
    """Base CLI command for handling Juju commands with write access."""

    @staticmethod
    def safe_parsed_args_output(parsed_args: argparse.Namespace) -> argparse.Namespace:
        """Remove sensitive information from output."""
        tmp_parsed_args = copy.deepcopy(parsed_args)
        tmp_parsed_args.filter.controllers = [controller.name for controller in parsed_args.filter.controllers]
        return tmp_parsed_args

    def run(self, parsed_args: argparse.Namespace) -> Optional[int]:
        """Execute CLI command for JujuCommands."""
        if not parsed_args.silent and not confirm(
            text=f"Continue on cmd: {self.name} parsed_args: {self.safe_parsed_args_output(parsed_args)}"
        ):
            return 0

        return super().run(parsed_args)
