import io
import uuid

import pytest
import yaml
from confuse import ConfigTypeError, ConfigView

from juju_spell.config import (
    SUBNET_REGEX,
    UUID_REGEX,
    Config,
    Connection,
    Controller,
    String,
    load_config,
    load_config_file,
    merge_configs,
)
from tests.unit.conftest import TEST_CONFIG, TEST_PERSONAL_CONFIG


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


def test_load_config(mocker, test_config_path, test_personal_config_path, mock_load_config_file_func, test_config):
    """Test load config."""
    mocker.patch("juju_spell.config.load_config_file", side_effect=mock_load_config_file_func)
    mocker.patch("juju_spell.config.merge_configs", return_value=test_config)
    config = load_config(test_config_path, test_personal_config_path)
    assert isinstance(config, Config)
    assert isinstance(config.controllers[0], Controller)
    assert isinstance(config.controllers[0].connection, Connection)
    assert config.controllers[0].name == "example_controller"
    assert config.controllers[0].endpoint == "10.1.1.46:17070"
    assert config.controllers[1].name == "example_controller_without_optional"
    assert config.controllers[1].endpoint == "10.1.1.47:17070"


def test_optional_config_values(test_config_path, test_personal_config_path):
    """Test optional config values and default values."""
    optional_keys = ["description", "tags", "connection"]  # list of keys
    default_values = {"risk": 5}  # key and value
    config = load_config(test_config_path, test_personal_config_path)
    controller = config.controllers[1]

    assert all(getattr(controller, key) is None for key in optional_keys)
    assert all(getattr(controller, key) == value for key, value in default_values.items())


@pytest.mark.parametrize(
    "config,personal_config,result",
    [
        (
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user1",
                    },
                ],
            },
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user2",
                    },
                ],
            },
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user2",
                    },
                ],
            },
        ),
        (
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user1",
                    },
                    {
                        "uuid": "723ff799-d50d-4a6f-b332-21954b86e422",
                        "username": "user3",
                    },
                ],
            },
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user2",
                    },
                ],
            },
            {
                "controllers": [
                    {
                        "uuid": "4f9988ff-3ff3-4644-9727-c47bb2d99588",
                        "username": "user2",
                    },
                    {
                        "uuid": "723ff799-d50d-4a6f-b332-21954b86e422",
                        "username": "user3",
                    },
                ],
            },
        ),
    ],
)
def test_merge_configs(config, personal_config, result):
    """Test merge_configs."""
    new_config = merge_configs(config, personal_config)
    assert new_config == result


@pytest.mark.parametrize("config_yaml", [TEST_CONFIG, TEST_PERSONAL_CONFIG])
def test_load_config_file(tmp_path, config_yaml):
    """Test load_config_file."""
    file_path = tmp_path / f"{uuid.uuid4()}.config"
    with open(file_path, "w", encoding="utf8") as file:
        file.write(config_yaml)

    result = load_config_file(file_path)
    assert result == yaml.safe_load(io.StringIO(config_yaml))
