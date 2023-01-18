"""Contains constants settings of the package."""
import os
import pathlib

APP_NAME = "juju-spell"
APP_VERSION = "0.0.1"
JUJUSPELL_DATA = pathlib.Path(
    os.environ.get(
        "JUJUSPELL_DATA",
        pathlib.Path(
            # The $HOME will be /snap/juju-spell/current after snap packaging.
            # We need to use $SNAP_REAL_HOME to get the real user's
            # home directory in snap.
            os.environ.get("SNAP_REAL_HOME", pathlib.Path.home())
        )
        / ".local/share/juju-spell",
    )
)

CONFIG_PATH = os.environ.get(
    "JUJUSPELL_CONFIG",
    pathlib.Path(JUJUSPELL_DATA / "config.yaml"),
)
PERSONAL_CONFIG_PATH = os.environ.get(
    "JUJUSPELL_PERSONAL_CONFIG", pathlib.Path(JUJUSPELL_DATA / "config.personal.yaml")
)
JUJUSPELL_DEFAULT_PORT_RANGE = range(17071, 17170)
