import re

from multijuju.settings import CONFIG_PATH

from .config import Config, load_config

# --filter "a=v1,v2,v3 b=v4,v5,v6"
FILTER_STR_REGEX = r"([^=]+)=([^=]+)(?:\s|$)"


def make_controllers_filter(filter_str):
    """Build filter func to config's controller."""

    def filter(controller):
        """Filter controllers."""
        for key, values in re.findall(
            FILTER_STR_REGEX,
            filter_str,
        ):
            if controller.get(key) in values.split(","):
                return True
        return False

    return filter


def get_filtered_config(filter_str) -> Config:
    config = load_config(CONFIG_PATH)
    if filter_str == "":
        return config
    controller_filter = make_controllers_filter(filter_str)
    config.controllers = list(filter(controller_filter, config.controllers))
    return config
