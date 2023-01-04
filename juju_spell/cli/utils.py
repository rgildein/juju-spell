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

"""Unilities."""
import re
import typing as t
from argparse import ArgumentTypeError
from functools import wraps
from gettext import gettext
from typing import List

from craft_cli import emit

from juju_spell.cli.exceptions import Abort
from juju_spell.config import Config
from juju_spell.filter import FILTER_EXPRESSION_REGEX, get_filtered_config

visible_prompt_func: t.Callable[[str], str] = input


def confirm(
    text: str,
    default: t.Optional[bool] = False,
    abort: bool = False,
    prompt_suffix: str = ": ",
    show_default: bool = True,
) -> bool:
    """Prompts for confirmation (yes/no question).

    If the user aborts the input by sending a interrupt signal this
    function will catch it and raise a :exc:`Abort` exception.

    :param text: the question to ask.
    :param default: The default value to use when no input is given. If
        ``None``, repeat until input is given.
    :param abort: if this is set to `True` a negative answer aborts the
                  exception by raising :exc:`Abort`.
    :param prompt_suffix: a suffix that should be added to the prompt.
    :param show_default: shows or hides the default value in the prompt.
    """
    prompt = text
    default_str = "y/n" if default is None else ("Y/n" if default else "y/N")
    if show_default is not None and show_default:
        prompt = f"{prompt} [{default_str}]"

    prompt = f"{prompt}{prompt_suffix}"

    while True:
        try:
            # Write the prompt separately so that we get nice
            # coloring through colorama on Windows
            emit.message(prompt.rstrip(" "))
            # Echo a space to stdout to work around an issue where
            # readline causes backspace to clear the whole line.
            value = visible_prompt_func(" ").lower().strip()
        except (KeyboardInterrupt, EOFError):
            raise Abort() from None
        if value in ("y", "yes"):
            return_value = True
        elif value in ("n", "no"):
            return_value = False
        elif default is not None and value == "":
            return_value = default
        else:
            emit.message(gettext("Error: invalid input"))
            continue
        break
    if abort and not return_value:
        raise Abort()
    return return_value


def confirm_it(func):
    @wraps(func)
    def _confirm(*args, **kwargs):
        if confirm("Continue on"):
            return func(*args, **kwargs)

    return _confirm


def parse_comma_separated_str(comma_separated_str: str) -> List[str]:
    """Parse comma separated string."""
    return comma_separated_str.strip().split(",")


def parse_filter(value: str) -> Config:
    """Type check for argument filter."""
    if not (re.findall(FILTER_EXPRESSION_REGEX, value) or len(value) == 0):
        raise ArgumentTypeError(f"Argument filter format wrong: {value}")

    filtered_config = get_filtered_config(value)
    if len(filtered_config.controllers) <= 0:
        raise ArgumentTypeError("No match controller")

    return filtered_config
