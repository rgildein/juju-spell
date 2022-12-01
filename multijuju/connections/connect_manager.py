import shutil
import tempfile
import uuid
from pathlib import Path


def generate_juju_data(juju_data: Path) -> None:
    """Generate JUJU_DATA directory."""
    # TODO: create all yaml files
    pass


class ConnectManager:
    """Connect manager is used to define JUJU_DATA directory and associated connections."""

    def __init__(self) -> None:
        """Initialize the ConnectManager."""
        self._juju_config = None  # TODO: add and use config argument
        self._uuid = uuid.uuid4()
        self._juju_data = None
        self._active = False

    def __enter__(self) -> "ConnectManager":
        """Enter ConnectManager."""
        self.activate()
        return self

    def __exit__(self, *args):
        """Leave ConnectManager."""
        self.deactivate()

    @property
    def active(self) -> bool:
        """Check if environment in active."""
        return self._active

    @property
    def juju_data(self) -> Path:
        """Get path to JUJU_DATA directory."""
        if not self._juju_data:
            tmpdir = tempfile.gettempdir()
            self._juju_data = Path(tmpdir, str(self._uuid))
            self._juju_data.mkdir()

        return self._juju_data

    @property
    def uuid(self) -> uuid.UUID:
        """Get UUID of connection."""
        return self._uuid

    def activate(self) -> "ConnectManager":
        """Activate environment for Juju.

        This function will define the JUJU_DATA environment with the clouds, controllers and accounts that Juju should
        connect to. At the same to
        - port-forward option: The port for the controller and specific units will be port-forwarded.
                               # TODO: add examples here or in config structure
        - sshuttle tunel option: Sshuttle can be created to redirect whole subnets.
                                 # TODO: add examples here or in config structure
        - JAAS option: use controllers registered with JAAS in JUJU_DATA generated phase
                       # TODO: add examples here or in config structure
        """
        generate_juju_data(self.juju_data)
        # TODO: set JUJU_DATA environment variable
        # TODO: port-forward or sshuttle
        self._active = True
        return self

    def deactivate(self):
        """Deactivate environment for Juju.

        Remove the JUJU_DATA environment and stop any port-forwarding or sshuttle tunel.
        """
        shutil.rmtree(self.juju_data)
        # TODO: unset JUJU_DATA environment variable
        # TODO: stop port-forwarding or sshuttle
        self._active = False
