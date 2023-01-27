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
from gettext import gettext
from typing import List

from craft_cli import emit

from juju_spell.exceptions import Abort
from juju_spell.filter import FILTER_EXPRESSION_REGEX

visible_prompt_func: t.Callable[[str], str] = input


def _get_value_from_prompt(prompt) -> str:
    """Get value from prompt."""
    try:
        # Write the prompt separately so that we get nice
        # coloring through colorama on Windows
        emit.message(prompt.rstrip(" "))
        # Echo a space to stdout to work around an issue where
        # readline causes backspace to clear the whole line.
        return visible_prompt_func(" ").strip()
    except (KeyboardInterrupt, EOFError):
        raise Abort() from None


def confirm(text: str, abort: bool = False) -> bool:
    """Prompts for confirmation (yes/no question).

    If the user aborts the input by sending an interrupt signal this
    function will catch it and raise a :exc:`Abort` exception.

    :param text: the question to ask.
    :param abort: if this is set to `True` a negative answer aborts the
                  exception by raising :exc:`Abort`.
    """
    prompt = f"{text}[Y/n]"

    while True:
        value = _get_value_from_prompt(prompt).lower()

        if value in ("y", "yes"):
            return True
        elif value in ("n", "no") and abort is False:
            return False
        elif value in ("n", "no") and abort:
            raise Abort()

        emit.message(gettext("Error: invalid input"))


def parse_comma_separated_str(comma_separated_str: str) -> List[str]:
    """Parse comma separated string."""
    result = comma_separated_str.split(",")
    return [obj.strip() for obj in result if obj]


def parse_filter(value: str) -> str:
    """Type check for argument filter."""
    if not (re.findall(FILTER_EXPRESSION_REGEX, value) or len(value) == 0):
        raise ArgumentTypeError(f"Argument filter format wrong: {value}")

    return value
