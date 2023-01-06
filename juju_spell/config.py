"""Configuration loader."""
import dataclasses
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import confuse
import yaml
from confuse import RootView

from juju_spell.utils import merge_list_of_dict_by_key

logger = logging.getLogger(__name__)

ENDPOINT_REGEX = (
    r"^(?:http)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # host
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
    r"(?::\d+)?"  # Optional[port]
    r"(?:/?|[/?]\S+)$"
)
API_ENDPOINT_REGEX = (
    r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # host
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
    r"(:\d+)?$"  # port
)
UUID_REGEX = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
CA_CERT_REGEX = r"^(-*)BEGIN CERTIFICATE(-*)\n((.|\n)*)\n(-*)END CERTIFICATE(-*)$"
SUBNET_REGEX = r"^([0-9]{1,3}\.){3}[0-9]{1,3}($|/(8|9|1[0-9]|2[0-9]|3[0-2]))$"
DESTINATION_REGEX = (
    r"^([A-Za-z]*@)?"  # Optional[user]
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # host
    r"([A-Za-z0-9,_,-,.]*)|"  # destination
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$"  # IP
)


class String(confuse.Template):
    """A template used to validate string with regex and provide custom error."""

    def __init__(self, pattern: str, message: str):
        """Initialize the String object."""
        super(String, self).__init__()
        self._regex = re.compile(pattern)
        self._message = message

    def convert(self, value: Any, view: confuse.ConfigView) -> str:
        """Check that the value is valid url."""
        if isinstance(value, str) and re.match(self._regex, value) is not None:
            return value

        self.fail(self._message, view, True)


class ControllerDict(confuse.MappingTemplate):
    """Controller template."""

    def value(self, view, template=None):
        """Get Controller object from dict."""
        output = super().value(view, template)
        return Controller(**output)


class ConnectionDict(confuse.MappingTemplate):
    """Connection template."""

    def value(self, view, template=None):
        """Get Connection object from dict."""
        output = super().value(view, template)
        return Connection(**output)


JUJUSPELL_CONFIG_TEMPLATE = confuse.MappingTemplate(
    {
        "controllers": confuse.Sequence(
            ControllerDict(
                {
                    "name": str,
                    "customer": str,
                    "owner": str,
                    "description": confuse.Optional(str),
                    "tags": confuse.Optional(confuse.Sequence(str)),
                    "risk": confuse.Choice(range(1, 6), default=5),
                    "endpoint": String(API_ENDPOINT_REGEX, "Invalid api endpoint definition"),
                    "ca_cert": String(CA_CERT_REGEX, "Invalid ca-cert format"),
                    "username": str,
                    "password": str,
                    "model_mapping": confuse.MappingTemplate(
                        {
                            "lma": confuse.String(default="lma"),
                            "default": confuse.String(default="production"),
                        }
                    ),
                    "connection": confuse.Optional(
                        ConnectionDict(
                            {
                                "subnets": confuse.Optional(
                                    confuse.Sequence(String(SUBNET_REGEX, "Invalid subnet definition"))
                                ),
                                "destination": String(DESTINATION_REGEX, "Invalid destination definition"),
                                "jumps": confuse.Optional(
                                    confuse.Sequence(String(DESTINATION_REGEX, "Invalid jump definition"))
                                ),
                            }
                        )
                    ),
                }
            )
        ),
    }
)


@dataclasses.dataclass
class Connection:
    destination: str
    jumps: Optional[List[str]] = None
    subnets: Optional[List[str]] = None


@dataclasses.dataclass
class GlobalController:
    """Controller without user's username and password."""

    name: str
    customer: str
    owner: str
    endpoint: str
    ca_cert: str
    username: str
    password: str
    model_mapping: Dict[str, str]
    # optional attributes and attributes with default value
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    risk: int = 5
    connection: Optional[Connection] = None


@dataclasses.dataclass
class PersonalController(GlobalController):
    """Controller with user identity."""

    username: str
    password: str


@dataclasses.dataclass
class Controller(PersonalController, GlobalController):
    pass


@dataclasses.dataclass
class Config:
    controllers: List[Controller]


def merge_configs(global_config, personal_config):
    # Merge personal and global config
    global_config["controllers"] = merge_list_of_dict_by_key(
        key="name",
        lists=[global_config["controllers"], personal_config["controllers"]],
    )
    return global_config


def load_config(global_config_path: Path, personal_config_path: Path) -> Config:
    """Load ad validate yaml config file."""
    with open(global_config_path, "r") as file:
        global_source = yaml.safe_load(file)
        logger.info("load global config file from %s path", global_config_path)

    with open(personal_config_path, "r") as file:
        personal_source = yaml.safe_load(file)
        logger.info("load personal config file from %s path", personal_config_path)

    # Merge personal and global config
    source = merge_configs(global_source, personal_source)

    # use confuse library only for validation
    _config = RootView([source])
    valid_config = _config.get(JUJUSPELL_CONFIG_TEMPLATE)  # TODO: catch exception here
    logger.info("config was validated")
    config = Config(**valid_config)

    return config
