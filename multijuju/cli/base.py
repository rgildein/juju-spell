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

import copy
import json

from craft_cli import BaseCommand, emit

from .utils import confirm


class BaseCMD(BaseCommand):
    """base cli command for handling contexts."""

    @staticmethod
    def safe_parsed_args_output(parsed_args):
        """Remove sensitive information from output."""
        tmp_parsed_args = copy.deepcopy(parsed_args)

        # Only display controller name when output
        if tmp_parsed_args.filter:
            tmp_parsed_args.filter.controllers = []
            for controller in parsed_args.filter.controllers:
                controller.ca_cert = None
                tmp_parsed_args.filter.controllers.append(controller.name)
        return tmp_parsed_args

    def run(self, parsed_args):
        if confirm(
            text=("Continue on" f" cmd: {self.name}" f" parsed_args: {self.safe_parsed_args_output(parsed_args)}",)
        ):
            self.before(parsed_args)
            retval = self.execute(parsed_args)
            self.format_output(retval)
            self.after(parsed_args)

    def format_output(self, retval):
        """Pretty formatter for output."""
        # TODO: pretty output, extract to own class
        # console output logic will be here yaml, json output will be central
        return emit.message(json.dumps(retval, default=vars, indent=1))

    def execute(self, parsed_args):
        pass

    def before(self, parsed_args):
        emit.message("-----------------------------------------------------")

    def after(self, parsed_args):
        emit.message("-----------------------------------------------------")
