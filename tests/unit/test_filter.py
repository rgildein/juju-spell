"""Test for filter."""

import pytest

from juju_spell.config import Config, Controller
from juju_spell.filter import get_filtered_config, make_controllers_filter


@pytest.mark.parametrize(
    "filter_expression,controllers,result",
    [
        (
            "name=controller-a",
            [
                Controller(
                    uuid="fc51ceb1-1fec-41b7-a7b0-5f7eee6d06dc",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="223eb7a5-7910-475f-a3f7-1c972a12f186",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    uuid="fc51ceb1-1fec-41b7-a7b0-5f7eee6d06dc",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
        ),
        (
            "name=controller-not-exists",
            [
                Controller(
                    uuid="fc51ceb1-1fec-41b7-a7b0-5f7eee6d06dc",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="41a5a12a-d357-485e-9910-2e84d90e1255",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [],
        ),
        (
            "user=admin customer=customer-a",
            [
                Controller(
                    uuid="44575f56-5591-4eb5-b7a5-df890a9518de",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="2cdff9e0-200f-41a0-a43f-2b21d0cd4484",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    uuid="44575f56-5591-4eb5-b7a5-df890a9518de",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="2cdff9e0-200f-41a0-a43f-2b21d0cd4484",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
        ),
        (
            "tags=a,b,c",
            [
                Controller(
                    uuid="a2ef8af6-9a6e-4a20-82dd-3cca327936c2",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                    tags=["a", "b", "c"],
                ),
            ],
            [
                Controller(
                    uuid="a2ef8af6-9a6e-4a20-82dd-3cca327936c2",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                    tags=["a", "b", "c"],
                ),
            ],
        ),
    ],
)
def test_make_controller_filter(
    filter_expression,
    controllers,
    result,
):
    """Test make_controllers_filter.

    We don't use real Controller class here is because
    we don't care the details in controller and also
    the Controller is dataclass which can get value with .get()
    """
    controller_filter = make_controllers_filter(filter_expression)
    filtered_controllers = list(filter(controller_filter, controllers))
    assert result == filtered_controllers


@pytest.mark.parametrize(
    "filter_expression,controllers,result_controllers",
    [
        (
            "name=controller-a",
            [
                Controller(
                    uuid="989dd4d6-c778-467a-95c9-11823dde0dbe",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="19a43de8-4c3b-44c4-aeb5-e03efc4ccefc",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    uuid="989dd4d6-c778-467a-95c9-11823dde0dbe",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
        ),
        (
            "tags=a,b,c",
            [
                Controller(
                    uuid="989dd4d6-c778-467a-95c9-11823dde0dbe",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    tags=["a", "b"],
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="19a43de8-4c3b-44c4-aeb5-e03efc4ccefc",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="17e806bf-7653-4a3a-befa-398a10d44cbc",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    tags=["d"],
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="f1e6b450-0121-459b-9f18-b25a89b36830",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    tags=["c"],
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    uuid="989dd4d6-c778-467a-95c9-11823dde0dbe",
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    tags=["a", "b"],
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    uuid="f1e6b450-0121-459b-9f18-b25a89b36830",
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    user="admin",
                    password="pwd",
                    tags=["c"],
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
        ),
    ],
)
def test_get_filtered_config(filter_expression, controllers, result_controllers):
    original_config = Config(controllers=controllers)
    config = get_filtered_config(original_config, filter_expression)
    assert config == Config(controllers=result_controllers)
