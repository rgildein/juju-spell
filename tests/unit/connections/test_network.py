import socket
import subprocess
from unittest import mock

import pytest


@pytest.mark.parametrize("return_code, exp_result", [(1, True), (0, False)])
@mock.patch("juju_spell.connections.network.socket.socket")
def test_is_port_free(mock_socket, return_code, exp_result):
    """Test function checking if port is free."""
    from juju_spell.connections.network import _is_port_free

    test_port = 17070
    mock_socket.return_value = tcp = mock.MagicMock()
    tcp.connect_ex.return_value = return_code

    result = _is_port_free(test_port)

    assert result == exp_result
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect_ex.assert_called_once_with(("localhost", test_port))
    tcp.close.assert_called_once()


@mock.patch("juju_spell.connections.network._is_port_free")
@mock.patch("juju_spell.connections.network.random.shuffle")
def test_get_free_tcp_port(mock_random_shuffle, mock_is_port_free):
    """Test getting free TCP port."""
    from juju_spell.connections.network import get_free_tcp_port

    exp_port = 17073
    mock_is_port_free.side_effect = [False, False, True, False]

    port = get_free_tcp_port(range(17071, 17075))

    mock_random_shuffle.assert_called_once_with([17071, 17072, 17073, 17074])
    mock_is_port_free.assert_has_calls(
        [mock.call(17071), mock.call(17072), mock.call(17073)]
    )
    assert port == exp_port


@mock.patch("juju_spell.connections.network._is_port_free")
def test_get_free_tcp_port_exception(mock_is_port_free):
    """Test getting free TCP port raising an Error."""
    from juju_spell.connections.network import get_free_tcp_port

    mock_is_port_free.return_value = False

    with pytest.raises(ValueError):
        get_free_tcp_port(range(17071, 17075))


@pytest.mark.parametrize(
    "args, exp_cmd",
    [
        (
            ("localhost:1234", "10.1.1.99:17070", "bastion"),
            ["ssh", "-N", "-L", "localhost:1234:10.1.1.99:17070", "", "bastion"],
        ),
        (
            ("localhost:1234", "10.1.1.99:17070", "bastion", ["bastion1", "bastion2"]),
            [
                "ssh",
                "-N",
                "-L",
                "localhost:1234:10.1.1.99:17070",
                "-J bastion1 -J bastion2",
                "bastion",
            ],
        ),
        (
            ("1234", "10.1.1.99:17070", "ubuntu@bastion"),
            ["ssh", "-N", "-L", "1234:10.1.1.99:17070", "", "ubuntu@bastion"],
        ),
    ],
)
@mock.patch(
    "juju_spell.connections.network.subprocess.Popen", return_value=mock.MagicMock
)
def test_ssh_port_forwarding_proc(mock_popen, args, exp_cmd):
    """Test create ssh tune for port forwarding."""
    from juju_spell.connections.network import ssh_port_forwarding_proc

    ssh_port_forwarding_proc(*args)
    mock_popen.assert_called_once_with(
        exp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


@pytest.mark.parametrize(
    "args, exp_cmd",
    [
        (
            (["10.1.1.0/24"], "bastion"),
            ["sshuttle", "-r", "bastion", "", "10.1.1.0/24"],
        ),
        (
            (["10.1.1.0/24"], "bastion", ["bastion1", "bastion2"]),
            [
                "sshuttle",
                "-r",
                "bastion",
                "-e 'ssh -J bastion1 -J bastion2'",
                "10.1.1.0/24",
            ],
        ),
        (
            (["10.1.1.0/24", "20.1.1.0/24"], "ubuntu@bastion"),
            ["sshuttle", "-r", "ubuntu@bastion", "", "10.1.1.0/24", "20.1.1.0/24"],
        ),
    ],
)
@mock.patch("juju_spell.connections.network.subprocess.Popen")
def test_sshuttle_proc(mock_popen, args, exp_cmd):
    """Test create sshuttle connection."""
    from juju_spell.connections.network import sshuttle_proc

    sshuttle_proc(*args)
    mock_popen.assert_called_once_with(
        exp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
