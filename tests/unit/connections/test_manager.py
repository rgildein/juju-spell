import io
import subprocess
import unittest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml

from juju_spell import config as juju_spell_config
from tests.unit.conftest import TEST_CONFIG, TEST_PERSONAL_CONFIG


@mock.patch("juju_spell.connections.connect_manager")
def test_connect_manager(mock_connect_manager):
    """Test predefined connect_manager object."""
    from juju_spell.connections import connect_manager

    assert connect_manager == mock_connect_manager


@mock.patch("juju_spell.connections.connect_manager")
def test_get_controller(mock_connect_manager, controller_config):
    """Test symlink for get_controller."""
    from juju_spell.connections import connect_manager

    connect_manager.get_controller(controller_config)
    mock_connect_manager.get_controller.assert_called_once_with(controller_config)


class TestConnectManager(unittest.IsolatedAsyncioTestCase):
    """Test case for ConnectManager class."""

    def setUp(self) -> None:
        """Set up before each test."""
        from juju_spell.connections import ConnectManager, connect_manager

        connect_manager._manager = None  # restart connect_manager
        self.connect_manager = ConnectManager()
        # NOTE: `@pytest.mark.usefixtures("controller_config")` do not work with
        # `IsolatedAsyncioTestCase`
        config = juju_spell_config.merge_configs(
            yaml.safe_load(io.StringIO(TEST_CONFIG)),
            yaml.safe_load(io.StringIO(TEST_PERSONAL_CONFIG)),
        )
        config["controllers"][0]["connection"] = juju_spell_config.Connection(
            **config["controllers"][0]["connection"]
        )
        self.controller_config_1 = juju_spell_config.Controller(
            **config["controllers"][0]
        )  # with connection
        self.controller_config_2 = juju_spell_config.Controller(
            **config["controllers"][1]
        )  # without connection

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.connect_manager.connections.clear()

    def test_new_object(self):
        """Test get new object."""
        from juju_spell.connections.manager import ConnectManager

        connect_manager1 = ConnectManager()
        connect_manager1.connections["test"] = MagicMock()
        connect_manager2 = ConnectManager()

        self.assertEqual(connect_manager1, connect_manager2)
        self.assertEqual(connect_manager1.connections, connect_manager2.connections)

    async def _test_connection(self, mock_controller, config, endpoint, **kwargs):
        """Help function to test connection."""
        mocked_controller = mock_controller.return_value = AsyncMock()
        controller = await self.connect_manager._connect(
            config, range(17071, 17170), **kwargs
        )

        assert controller == mocked_controller
        mocked_controller.connect.assert_called_once_with(
            endpoint=endpoint,
            username=config.username,
            password=config.password,
            cacert=config.ca_cert,
        )
        assert config.name in self.connect_manager.connections

    @mock.patch("juju_spell.connections.manager.juju.Controller")
    async def test_connect(self, mock_controller):
        """Test connection with direct access."""
        config = self.controller_config_2
        await self._test_connection(mock_controller, config, config.endpoint)

    @mock.patch("juju_spell.connections.manager.ssh_port_forwarding_proc")
    @mock.patch("juju_spell.connections.manager.get_free_tcp_port", return_value=17070)
    @mock.patch("juju_spell.connections.manager.juju.Controller")
    async def test_connect_ssh_tunel(
        self, mock_controller, mock_get_free_tcp_port, mock_ssh_port_forwarding_proc
    ):
        """Test connection with ssh tunnel."""
        config = self.controller_config_1

        await self._test_connection(mock_controller, config, "localhost:17070")
        mock_get_free_tcp_port.assert_called_once()
        mock_ssh_port_forwarding_proc.assert_called_once_with(
            "localhost:17070",
            config.endpoint,
            config.connection.destination,
            config.connection.jumps,
        )

    @mock.patch("juju_spell.connections.manager.sshuttle_proc")
    @mock.patch("juju_spell.connections.manager.juju.Controller")
    async def test_connect_sshuttle(self, mock_controller, mock_sshuttle_proc):
        """Test connection with sshuttle."""
        config = self.controller_config_1

        await self._test_connection(
            mock_controller, config, config.endpoint, sshuttle=True
        )
        mock_sshuttle_proc.assert_called_once_with(
            config.connection.subnets,
            config.connection.destination,
            config.connection.jumps,
        )

    async def test_clean(self):
        """Test clean function."""
        from juju_spell.connections.manager import Connection

        # define mecked connections
        connections = []
        for i in range(10):
            controller = AsyncMock()
            connection_process = None if i >= 5 else MagicMock(spec=subprocess.Popen)
            connection = Connection(controller, connection_process)
            self.connect_manager.connections[f"test-{i}"] = connection
            connections.append(connection)

        assert len(self.connect_manager.connections) == 10

        # test clean functions
        await self.connect_manager.clean()
        assert len(self.connect_manager.connections) == 0
        for connection in connections:
            connection.controller.disconnect.assert_called_once()
            if connection.connection_process is not None:
                connection.connection_process.terminate.assert_called_once()

    async def test_get_controller_invalid_controller_config(self):
        """Test function to get controller with invalid controller config."""
        with pytest.raises(AssertionError):
            await self.connect_manager.get_controller({"name": "test"})

    async def test_get_controller_new_controller(self):
        """Test function to get controller."""
        config = self.controller_config_1
        self.connect_manager._connect = mock_connect = AsyncMock()

        controller = await self.connect_manager.get_controller(config, reconnect=False)

        mock_connect.assert_called_once_with(config, range(17071, 17170), False)
        assert controller == mock_connect.return_value

    async def test_get_controller_reconnect(self):
        """Test function to get controller with reconnection."""
        config = self.controller_config_1
        self.connect_manager._connect = mock_connect = AsyncMock()
        self.connect_manager.connections[config.name] = mocked_connection = AsyncMock()
        mocked_connection.controller.is_connected = lambda: True

        controller = await self.connect_manager.get_controller(config, reconnect=True)

        mocked_connection.controller.disconnect.assert_called_once()
        mock_connect.assert_called_once_with(config, range(17071, 17170), False)
        assert controller == mock_connect.return_value

    async def test_get_controller_auto_reconnect(self):
        """Test function to get controller with auto reconnection."""
        config = self.controller_config_1
        self.connect_manager._connect = mock_connect = AsyncMock()
        mocked_connection = AsyncMock()
        mocked_connection.controller = mock_controller = MagicMock()
        mock_controller.is_connected.return_value = False
        self.connect_manager.connections[config.name] = mocked_connection

        controller = await self.connect_manager.get_controller(config, reconnect=False)

        mock_connect.assert_called_once_with(config, range(17071, 17170), False)
        assert controller == mock_connect.return_value

    async def test_get_controller_existing_controller(self):
        """Test function to get controller, which already exists."""
        config = self.controller_config_1
        self.connect_manager.connections[config.name] = mocked_connection = AsyncMock()
        mocked_connection.controller.is_connected = lambda: True

        controller = await self.connect_manager.get_controller(config)

        assert controller == mocked_connection.controller
