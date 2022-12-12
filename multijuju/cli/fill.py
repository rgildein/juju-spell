"""Filter function that handle argparse type."""
from argparse import ArgumentParser
from typing import List

from multijuju.config import Config


def parse_comma_separated_str(comma_separated_str: str) -> List[str]:
    """Parse comma separated string."""
    return comma_separated_str.strip().split(",")


def parse_filter(value: str) -> Config:
    """Type check for argument filter."""
    # TODO: Implement later
    return value


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
        nargs="+",
        help="Comma separated controller filter string",
    )
