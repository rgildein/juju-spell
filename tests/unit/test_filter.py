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
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
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
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
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
            "username=admin customer=customer-a",
            [
                Controller(
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
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
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
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
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
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
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
                Controller(
                    name="controller-b",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
            [
                Controller(
                    name="controller-a",
                    customer="customer-a",
                    owner="owner-a",
                    endpoint="localhost:17070",
                    ca_cert="",
                    username="admin",
                    password="pwd",
                    model_mapping={
                        "lma": "monitoring",
                        "default": "production",
                    },
                ),
            ],
        ),
    ],
)
def test_get_filtered_config(
    mocker,
    filter_expression,
    controllers,
    result_controllers,
):
    mocker.patch("juju_spell.filter.load_config", return_value=Config(controllers=controllers))
    config = get_filtered_config(filter_expression=filter_expression)
    assert config == Config(controllers=result_controllers)
