import pytest
from confuse import ConfigTypeError, ConfigView

from multijuju.config import (
    SUBNET_REGEX,
    UUID_REGEX,
    Config,
    Connection,
    Controller,
    String,
    load_config,
)


@pytest.mark.parametrize(
    "regex, value",
    [
        (r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", "1.2.3.4"),
        (SUBNET_REGEX, "1.2.3.0/24"),
        (UUID_REGEX, "e53042ba-8ff5-456c-85b8-f7fef37bff5c"),
    ],
)
def test_string(regex, value):
    """Test custom string option."""
    string = String(regex, "test message")
    view = ConfigView()
    assert string.convert(value, view) == value


@pytest.mark.parametrize("regex, value", [(SUBNET_REGEX, "1.2"), (UUID_REGEX, "1-2-3-4-5")])
def test_string_exception(regex, value):
    """Test custom string option."""
    string = String(regex, "test message")
    view = ConfigView()
    with pytest.raises(ConfigTypeError):
        string.convert(value, view)


def test_load_config(test_config_path):
    """Test load config."""
    config = load_config(test_config_path)
    assert isinstance(config, Config)
    assert isinstance(config.controllers[0], Controller)
    assert isinstance(config.controllers[0].connection, Connection)
    assert config.controllers[0].name == "example_controller"
    assert config.controllers[0].endpoint == "10.1.1.46:17070"
    assert config.controllers[1].name == "example_controller_without_optional"
    assert config.controllers[1].endpoint == "10.1.1.47:17070"


def test_optional_config_values(test_config_path):
    """Test optional config values and default values."""
    optional_keys = ["description", "tags", "connection"]  # list of keys
    default_values = {"risk": 5}  # key and value
    config = load_config(test_config_path)
    controller = config.controllers[1]

    assert all(getattr(controller, key) is None for key in optional_keys)
    assert all(getattr(controller, key) == value for key, value in default_values.items())
