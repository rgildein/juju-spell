"""Filter logic."""
import re

from multijuju.settings import CONFIG_PATH

from .config import Config, Controller, load_config

# --filter "a=v1,v2,v3 b=v4,v5,v6"
FILTER_EXPRESSION_REGEX = r"([^=]+)=([^=]+)(?:\s|$)"


def make_controllers_filter(filter_expression):
    """Build filter func to config's controller."""

    def filter(controller: Controller):
        """Filter controllers."""
        # If the filter_str is "a=v1,v2,v3 b=v4,v5,v6"
        # This will iterate over keys [a,b] to check the value
        # inside controller match the values list a in [v1,v2,v3]
        # and b in [v4,v5,v6].
        for key, values in re.findall(
            FILTER_EXPRESSION_REGEX,
            filter_expression,
        ):
            if not controller.get(key) in values.split(","):
                return False
        return True

    return filter


def get_filtered_config(filter_expression: str) -> Config:
    config = load_config(CONFIG_PATH)
    if filter_expression == "":
        return config
    controller_filter = make_controllers_filter(filter_expression)
    config.controllers = list(filter(controller_filter, config.controllers))
    return config
