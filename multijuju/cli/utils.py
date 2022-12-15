"""Unilities."""
import typing as t
from functools import wraps
from gettext import gettext

from craft_cli import emit

from .exceptions import Abort

visible_prompt_func: t.Callable[[str], str] = input


def confirm(
    text: str,
    default: t.Optional[bool] = False,
    abort: bool = False,
    prompt_suffix: str = ": ",
    show_default: bool = True,
    silent: bool = False,
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
    :param silent: Skip the check
    """
    if silent:
        return True
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
