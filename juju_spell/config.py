"""Configuration loader."""
import dataclasses
import logging
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import confuse
import yaml
from confuse import RootView

from juju_spell.settings import JUJUSPELL_DEFAULT_PORT_RANGE
from juju_spell.utils import merge_list_of_dict_by_key

logger = logging.getLogger(__name__)

ENDPOINT_REGEX = (
    r"^(?:http)s?://"  # http:// or https://
    # host
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
    r"(?::\d+)?"  # Optional[port]
    r"(?:/?|[/?]\S+)$"
)
API_ENDPOINT_REGEX = (
    # host
    r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
    r"(:\d+)?$"  # port
)
UUID_REGEX = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
CA_CERT_REGEX = r"^(-*)BEGIN CERTIFICATE(-*)\n((.|\n)*)\n(-*)END CERTIFICATE(-*)$"
SUBNET_REGEX = r"^([0-9]{1,3}\.){3}[0-9]{1,3}($|/(8|9|1[0-9]|2[0-9]|3[0-2]))$"
DESTINATION_REGEX = (
    r"^([A-Za-z]*@)?"  # Optional[user]
    # host
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"([A-Za-z0-9,_,-,.]*)|"  # destination
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$"  # IP
)
PORT_RANGE = (
    r"^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|"
    r"(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))"
    r":"  # delimiter
    r"((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|"
    r"([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"
)


class String(confuse.Template):
    """A template used to validate string with regex and provide custom error."""

    def __init__(self, pattern: str, message: str, default: Optional[str] = None):
        """Initialize the String object."""
        super(String, self).__init__(default=default)
        self._regex = re.compile(pattern)
        self._message = message

    def convert(self, value: Any, view: confuse.ConfigView) -> str:
        """Check that the value is valid url."""
        if isinstance(value, str) and re.match(self._regex, value) is not None:
            return value

        self.fail(self._message, view, True)


class PortRange(String):
    """A template specific for port range."""

    def convert(self, value: Any, view: confuse.ConfigView) -> range:
        """Check and convert port-range string to tuple."""
        value = super().convert(value, view)
        start_port, end_port = value.split(":")
        return range(int(start_port), int(end_port))


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
        "connection": confuse.MappingTemplate(
            {
                "port-range": confuse.Optional(
                    PortRange(
                        PORT_RANGE,
                        "Invalid port-range definition",
                        default=JUJUSPELL_DEFAULT_PORT_RANGE,
                    )
                ),
            }
        ),
        "controllers": confuse.Sequence(
            ControllerDict(
                {
                    "uuid": String(UUID_REGEX, "Invalid uuid definition"),
                    "name": str,
                    "customer": str,
                    "owner": str,
                    "description": confuse.Optional(str),
                    "tags": confuse.Optional(confuse.Sequence(str)),
                    "risk": confuse.Choice(range(1, 6), default=5),
                    "endpoint": String(
                        API_ENDPOINT_REGEX, "Invalid api endpoint definition"
                    ),
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
                                    confuse.Sequence(
                                        String(
                                            SUBNET_REGEX, "Invalid subnet definition"
                                        )
                                    )
                                ),
                                "destination": String(
                                    DESTINATION_REGEX, "Invalid destination definition"
                                ),
                                "jumps": confuse.Optional(
                                    confuse.Sequence(
                                        String(
                                            DESTINATION_REGEX, "Invalid jump definition"
                                        )
                                    )
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
class Controller:
    """Juju Controller."""

    uuid: uuid.UUID
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
class Config:
    controllers: List[Controller]
    connection: Optional[Dict[str, Any]] = None


def _validate_config(source: Dict[str, Any]) -> Config:
    """Validate config.

    Using confuse library to validate config.
    """
    _config = RootView([source])
    valid_config = _config.get(JUJUSPELL_CONFIG_TEMPLATE)  # TODO: catch exception here
    logger.info("config was validated")
    config = Config(**valid_config)
    return config


def merge_configs(config: Dict, personal_config: Dict):
    # Merge personal and global config
    config["controllers"] = merge_list_of_dict_by_key(
        key="uuid",
        lists=[config["controllers"], personal_config["controllers"]],
    )
    return config


def load_config_file(path):
    with open(path, "r") as file:
        source = yaml.safe_load(file)
        logger.info("load config file from %s path", path)
    return source


def load_config(
    config_path: Path, personal_config_path: Optional[Path] = None
) -> Config:
    """Load ad validate yaml config file."""
    source = load_config_file(config_path)
    if personal_config_path and personal_config_path.exists():
        personal_source = load_config_file(personal_config_path)
        # Merge personal and default config
        source = merge_configs(source, personal_source)

    config = _validate_config(source)
    return config
