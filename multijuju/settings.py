"""Contains constants settings of the package."""
import os
import pathlib

APP_NAME = "MultiJuju"
APP_VERSION = "0.0.1"
MULTIJUJU_DATA = pathlib.Path(os.environ.get("MULTIJUJU_DATA", pathlib.Path.home() / ".local/share/multijuju"))

CONFIG_PATH = pathlib.Path(MULTIJUJU_DATA / "config.yaml")
