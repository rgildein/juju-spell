from pathlib import Path

import mock

from multijuju.connections import connect_manager
from multijuju.connections.connect_manager import generate_juju_data


def crete_test_juju_data(path: Path) -> None:
    """Generate test JUJU_DATA directory structure with empty files and ssh directory."""
    (path / "accounts.yaml").touch()
    (path / "clouds.yaml").touch()
    (path / "controllers.yaml").touch()
    (path / "models.yaml").touch()
    (path / "ssh").mkdir()
    (path / "ssh" / "juju_id_rsa").touch()
    (path / "ssh" / "juju_id_rsa.pub").touch()


def test_generate_juju_data(tmp_path):
    """Test generate juju_data function."""
    generate_juju_data(tmp_path)


@mock.patch.object(connect_manager, "uuid")
def test_connect_manage_init(mock_uuid):
    """Test initialization of ConnectManager."""
    mock_uuid.uuid4.return_value = "1234"
    manager = connect_manager.ConnectManager()

    mock_uuid.uuid4.assert_called_once()
    assert manager.uuid == "1234"


@mock.patch.object(connect_manager, "generate_juju_data", side_effect=crete_test_juju_data)
@mock.patch.object(connect_manager, "uuid")
@mock.patch.object(connect_manager, "tempfile")
def test_connect_manager_activation(mock_tempfile, mock_uuid, mock_generate_juju_data, tmp_path):
    """Test connect_manager.activate."""
    mock_uuid.uuid4.return_value = test_uuid = "1234"
    mock_tempfile.gettempdir.return_value = tmp_path
    manager = connect_manager.ConnectManager()
    manager.activate()

    mock_generate_juju_data.assert_called_once_with(tmp_path / test_uuid)
    assert (tmp_path / test_uuid).exists()
    assert manager.active

    manager.deactivate()


@mock.patch.object(connect_manager, "generate_juju_data", side_effect=crete_test_juju_data)
@mock.patch.object(connect_manager, "uuid")
@mock.patch.object(connect_manager, "tempfile")
def test_connect_manager_deactivation(mock_tempfile, mock_uuid, _, tmp_path):
    """Test connect_manager.deactivation."""
    mock_uuid.uuid4.return_value = test_uuid = "1234"
    mock_tempfile.gettempdir.return_value = tmp_path
    manager = connect_manager.ConnectManager()
    manager.activate()
    assert (tmp_path / test_uuid / "accounts.yaml").exists()
    assert (tmp_path / test_uuid / "ssh").exists()
    manager.deactivate()

    assert not (tmp_path / test_uuid).exists()
    assert not manager.active


@mock.patch.object(connect_manager, "generate_juju_data", side_effect=crete_test_juju_data)
@mock.patch.object(connect_manager, "uuid")
@mock.patch.object(connect_manager, "tempfile")
def test_connect_manager_as_context_manager(mock_tempfile, mock_uuid, _, tmp_path):
    """Test usage of ConnectManager as ContextManager."""
    mock_uuid.uuid4.return_value = test_uuid = "1234"
    mock_tempfile.gettempdir.return_value = tmp_path
    with connect_manager.ConnectManager() as manager:
        assert manager.uuid == "1234"
        assert (tmp_path / test_uuid).exists()
        assert manager.active

    assert not manager.active
