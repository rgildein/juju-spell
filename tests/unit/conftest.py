import io
from pathlib import Path

import pytest
import yaml

from juju_spell.config import Connection, Controller, merge_configs

TEST_GLOBAL_CONFIG = """
controllers:
  - name: example_controller
    customer: example_customer
    owner: Gandalf
    description: some nice notes about controllers and models
    tags: ["test"]
    risk: 5
    endpoint: 10.1.1.46:17070
    ca_cert: |
        -----BEGIN CERTIFICATE-----
        1234
        -----END CERTIFICATE-----
    model_mapping:
      lma: monitoring
      default: production
    connection:
      destination: ubuntu@10.1.1.99
      subnets:  # optional (sshuttle)
        - 10.1.1.0/24
        - 20.1.1.0/24
      jumps:
        - bastion
  - name: example_controller_without_optional
    customer: example_customer
    owner: Gandalf
    endpoint: 10.1.1.47:17070
    ca_cert: |
        -----BEGIN CERTIFICATE-----
        1234
        -----END CERTIFICATE-----
    model_mapping:
      lma: monitoring
      default: production
"""

TEST_PERSONAL_CONFIG = """
controllers:
  - name: example_controller
    username: admin
    password: pass1234
  - name: example_controller_without_optional
    username: admin
    password: pass1234
"""


@pytest.fixture
def test_global_config_path(tmp_path) -> Path:
    """Return path to test global config."""
    path = tmp_path / "global_config.yaml"
    with open(path, "w") as file:
        file.write(TEST_GLOBAL_CONFIG)

    return path


@pytest.fixture
def test_personal_config_path(tmp_path) -> Path:
    """Return path to test personal config."""
    path = tmp_path / "personal_config.yaml"
    with open(path, "w") as file:
        file.write(TEST_PERSONAL_CONFIG)

    return path


@pytest.fixture
def test_config():
    """Return config file as dict."""
    config = merge_configs(
        yaml.safe_load(io.StringIO(TEST_GLOBAL_CONFIG)),
        yaml.safe_load(io.StringIO(TEST_PERSONAL_CONFIG)),
    )
    return config


@pytest.fixture
def controller_config(test_config):
    """Return first controller configuration form test config."""
    controller = test_config["controllers"][0]
    controller["connection"] = Connection(controller["connection"])
    return Controller(**controller)
