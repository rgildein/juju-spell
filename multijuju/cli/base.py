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

"""multijuju base cli command."""
import argparse
import copy
import json
from typing import Any

from craft_cli import BaseCommand, emit
from craft_cli.dispatcher import _CustomArgumentParser

from .utils import confirm


class BaseCMD(BaseCommand):
    """base cli command for handling contexts."""

    def fill_parser(self, parser: _CustomArgumentParser) -> None:
        parser.add_argument(
            "--silent",
            default=False,
            action="store_true",
            help="This will skip all the confirm check.",
        )

    @staticmethod
    def safe_parsed_args_output(parsed_args: argparse.Namespace) -> argparse.Namespace:
        """Remove sensitive information from output."""
        tmp_parsed_args = copy.deepcopy(parsed_args)

        # Only display controller name when output
        if hasattr(tmp_parsed_args, "filter"):
            tmp_parsed_args.filter.controllers = [controller.name for controller in parsed_args.filter.controllers]

        return tmp_parsed_args

    def run(self, parsed_args: argparse.Namespace) -> None:
        if parsed_args.silent or confirm(
            text=f"Continue on cmd: {self.name} parsed_args: {self.safe_parsed_args_output(parsed_args)}"
        ):
            self.before(parsed_args)
            retval = self.execute(parsed_args)
            self.format_output(retval)
            self.after(parsed_args)

    def format_output(self, retval: Any) -> Any:
        """Pretty formatter for output."""
        # TODO: pretty output, extract to own class
        # console output logic will be here yaml, json output will be central
        return emit.message(json.dumps(retval, default=vars, indent=1))

    def execute(self, parsed_args: argparse.Namespace) -> None:
        pass

    def before(self, parsed_args: argparse.Namespace) -> None:
        pass

    def after(self, parsed_args: argparse.Namespace) -> None:
        pass
