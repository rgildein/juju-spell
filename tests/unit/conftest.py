import io
from pathlib import Path
from unittest import mock

import pytest
import yaml

from multijuju.config import Config

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
    model_mappings:
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
    model_mappings:
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
    with mock.patch("multijuju.config.load_config") as mock_load_config:
        config = yaml.safe_load(io.StringIO(TEST_CONFIG))
        mock_load_config.return_value = Config(**config)
        yield config
