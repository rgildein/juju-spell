"""Filter function that handle argparse type."""
import re
from argparse import ArgumentParser, ArgumentTypeError
from typing import List

from multijuju.config import Config
from multijuju.filter import FILTER_EXPRESSION_REGEX, get_filtered_config


def parse_comma_separated_str(comma_separated_str: str) -> List[str]:
    """Parse comma separated string."""
    return comma_separated_str.strip().split(",")


def parse_filter(value: str) -> Config:
    """Type check for argument filter."""
    if not (
        re.findall(
            FILTER_EXPRESSION_REGEX,
            value,
        )
        or len(value) == 0  # no filter
    ):
        raise ArgumentTypeError(f"Argument filter format wrong: {value}")

    filtered_config = get_filtered_config(value)
    if len(filtered_config.controllers) <= 0:
        raise ArgumentTypeError("No match controller")
    return filtered_config


def add_assignment_argument(parser: ArgumentParser):
    """Add assignment required arguments to ArgumentParser."""
    parser.add_argument(
        "--run-type",
        type=str,
        default="serial",
        help="parallel,batch or serial",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="./multi-juju-config.yaml",
        help="config file path",
    )


def add_connection_manager_argument(parser: ArgumentParser):
    """Add connection manager required arguments to ArgumentParser."""
    parser.add_argument(
        "--filter",
        type=parse_filter,
        required=False,
        default="",
        help="""Key-value pair comma separated string in double quotes e.g., "a=1,2,3 b=4,5,6". """,
    )


def add_model_argument(parser: ArgumentParser):
    """Add juju models filter to ArgumentParser."""
    parser.add_argument(
        "--models",
        type=parse_comma_separated_str,
        help="model filter",
    )
