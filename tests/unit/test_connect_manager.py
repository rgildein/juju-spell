import io
import socket
import subprocess
import unittest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml

from multijuju import config as multijuju_config
from tests.unit.conftest import TEST_CONFIG


@mock.patch("multijuju.connections.manager.socket.socket")
def test_get_free_tcp_port(mock_socket):
    """Test getting free TCP port."""
    from multijuju.connections.manager import get_free_tcp_port

    exp_port = 1999
    mock_socket.return_value = mock_tcp = MagicMock()
    mock_tcp.getsockname.return_value = (None, exp_port)
    port = get_free_tcp_port()

    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_tcp.bind.assert_called_once_with(("", 0))
    mock_tcp.getsockname.assert_called_once()
    mock_tcp.close.assert_called_once()
    assert port == exp_port


@pytest.mark.parametrize(
    "args, exp_cmd",
    [
        (
            ("localhost:1234", "10.1.1.99:17070", "bastion"),
            ["ssh", "-N", "-L", "localhost:1234:10.1.1.99:17070", "", "bastion"],
        ),
        (
            ("localhost:1234", "10.1.1.99:17070", "bastion", ["bastion1", "bastion2"]),
            ["ssh", "-N", "-L", "localhost:1234:10.1.1.99:17070", "-J bastion1 -J bastion2", "bastion"],
        ),
        (
            ("1234", "10.1.1.99:17070", "ubuntu@bastion"),
            ["ssh", "-N", "-L", "1234:10.1.1.99:17070", "", "ubuntu@bastion"],
        ),
    ],
)
@mock.patch("multijuju.connections.manager.subprocess.Popen", return_value=MagicMock)
def test_ssh_port_forwarding_proc(mock_popen, args, exp_cmd):
    """Test create ssh tune for port forwarding."""
    from multijuju.connections.manager import ssh_port_forwarding_proc

    ssh_port_forwarding_proc(*args)
    mock_popen.assert_called_once_with(exp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@pytest.mark.parametrize(
    "args, exp_cmd",
    [
        ((["10.1.1.0/24"], "bastion"), ["sshuttle", "-r", "bastion", "", "10.1.1.0/24"]),
        (
            (["10.1.1.0/24"], "bastion", ["bastion1", "bastion2"]),
            ["sshuttle", "-r", "bastion", "-e 'ssh -J bastion1 -J bastion2'", "10.1.1.0/24"],
        ),
        (
            (["10.1.1.0/24", "20.1.1.0/24"], "ubuntu@bastion"),
            ["sshuttle", "-r", "ubuntu@bastion", "", "10.1.1.0/24", "20.1.1.0/24"],
        ),
    ],
)
@mock.patch("multijuju.connections.manager.subprocess.Popen")
def test_sshuttle_proc(mock_popen, args, exp_cmd):
    """Test create sshuttle connection."""
    from multijuju.connections.manager import sshuttle_proc

    sshuttle_proc(*args)
    mock_popen.assert_called_once_with(exp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@mock.patch("multijuju.connections.connect_manager")
def test_connect_manager(mock_connect_manager):
    """Test predefined connect_manager object."""
    from multijuju.connections import connect_manager

    assert connect_manager == mock_connect_manager


@mock.patch("multijuju.connections.connect_manager")
def test_get_controller(mock_connect_manager, controller_config):
    """Test symlink for get_controller."""
    from multijuju.connections import connect_manager

    connect_manager.get_controller(controller_config)
    mock_connect_manager.get_controller.assert_called_once_with(controller_config)


class TestConnectManager(unittest.IsolatedAsyncioTestCase):
    """Test case for ConnectManager class."""

    def setUp(self) -> None:
        """Set up before each test."""
        from multijuju.connections import ConnectManager, connect_manager

        connect_manager._manager = None  # restart connect_manager
        self.connect_manager = ConnectManager()
        # `@pytest.mark.usefixtures("controller_config")` do not work with `IsolatedAsyncioTestCase`
        config = yaml.safe_load(io.StringIO(TEST_CONFIG))
        config["controllers"][0]["connection"] = multijuju_config.Connection(**config["controllers"][0]["connection"])
        self.controller_config_1 = multijuju_config.Controller(**config["controllers"][0])  # with connection
        self.controller_config_2 = multijuju_config.Controller(**config["controllers"][1])  # without connection

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.connect_manager.connections.clear()

    def test_new_object(self):
        """Test get new object."""
        from multijuju.connections.manager import ConnectManager

        connect_manager1 = ConnectManager()
        connect_manager1.connections["test"] = MagicMock()
        connect_manager2 = ConnectManager()

        self.assertEqual(connect_manager1, connect_manager2)
        self.assertEqual(connect_manager1.connections, connect_manager2.connections)

    async def _test_connection(self, mock_controller, config, endpoint, **kwargs):
        """Help function to test connection."""
        mocked_controller = mock_controller.return_value = AsyncMock()
        controller = await self.connect_manager._connect(config, **kwargs)

        assert controller == mocked_controller
        mocked_controller.connect.assert_called_once_with(
            endpoint=endpoint,
            username=config.username,
            password=config.password,
            cacert=config.ca_cert,
        )
        assert config.name in self.connect_manager.connections

    @mock.patch("multijuju.connections.manager.juju.Controller")
    async def test_connect(self, mock_controller):
        """Test connection with direct access."""
        config = self.controller_config_2
        await self._test_connection(mock_controller, config, config.endpoint)

    @mock.patch("multijuju.connections.manager.ssh_port_forwarding_proc")
    @mock.patch("multijuju.connections.manager.get_free_tcp_port", return_value=17070)
    @mock.patch("multijuju.connections.manager.juju.Controller")
    async def test_connect_ssh_tunel(self, mock_controller, mock_get_free_tcp_port, mock_ssh_port_forwarding_proc):
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

    @mock.patch("multijuju.connections.manager.sshuttle_proc")
    @mock.patch("multijuju.connections.manager.juju.Controller")
    async def test_connect_sshuttle(self, mock_controller, mock_sshuttle_proc):
        """Test connection with sshuttle."""
        config = self.controller_config_1

        await self._test_connection(mock_controller, config, config.endpoint, sshuttle=True)
        mock_sshuttle_proc.assert_called_once_with(
            config.connection.subnets,
            config.connection.destination,
            config.connection.jumps,
        )

    async def test_clean(self):
        """Test clean function."""
        from multijuju.connections.manager import Connection

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

        mock_connect.assert_called_once_with(config, False)
        assert controller == mock_connect.return_value

    async def test_get_controller_reconnect(self):
        """Test function to get controller with reconnection."""
        config = self.controller_config_1
        self.connect_manager._connect = mock_connect = AsyncMock()
        self.connect_manager.connections[config.name] = mocked_connection = AsyncMock()
        mocked_connection.controller.is_connected = lambda: True

        controller = await self.connect_manager.get_controller(config, reconnect=True)

        mocked_connection.controller.disconnect.assert_called_once()
        mock_connect.assert_called_once_with(config, False)
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

        mock_connect.assert_called_once_with(config, False)
        assert controller == mock_connect.return_value

    async def test_get_controller_existing_controller(self):
        """Test function to get controller, which already exists."""
        config = self.controller_config_1
        self.connect_manager.connections[config.name] = mocked_connection = AsyncMock()
        mocked_connection.controller.is_connected = lambda: True

        controller = await self.connect_manager.get_controller(config)

        assert controller == mocked_connection.controller
