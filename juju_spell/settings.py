"""Contains constants settings of the package."""
import os
import pathlib

APP_NAME = "juju-spell"
APP_VERSION = "0.0.1"
JUJUSPELL_DATA = pathlib.Path(os.environ.get("JUJUSPELL_DATA", pathlib.Path.home() / ".local/share/juju-spell"))

CONFIG_PATH = os.environ.get(
    "JUJUSPELL_CONFIG",
    pathlib.Path(JUJUSPELL_DATA / "config.yaml"),
)
PERSONAL_CONFIG_PATH = os.environ.get(
    "JUJUSPELL_PERSONAL_CONFIG", pathlib.Path(JUJUSPELL_DATA / "config.personal.yaml")
)
