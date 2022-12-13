import io
from pathlib import Path

import pytest
import yaml

from multijuju.config import Connection, Controller

TEST_CONFIG = """
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
    username: admin
    password: pass1234
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
    username: admin
    password: pass1234
    model_mapping:
      lma: monitoring
      default: production
"""


@pytest.fixture
def test_config_path(tmp_path) -> Path:
    """Return path to test config."""
    path = tmp_path / "config.yaml"
    with open(path, "w") as file:
        file.write(TEST_CONFIG)

    return path


@pytest.fixture
def test_config(tmp_path):
    """Return config file as dict."""
    config = yaml.safe_load(io.StringIO(TEST_CONFIG))
    return config


@pytest.fixture
def controller_config(test_config):
    """Return first controller configuration form test config."""
    controller = test_config["controllers"][0]
    controller["connection"] = Connection(controller["connection"])
    return Controller(**controller)
