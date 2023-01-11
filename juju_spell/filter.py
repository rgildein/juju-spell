"""Filter logic."""
import re
import typing as t
from dataclasses import asdict

from juju_spell.settings import CONFIG_PATH, PERSONAL_CONFIG_PATH

from .config import Config, Controller, load_config

# --filter "a=v1,v2,v3 b=v4,v5,v6"
FILTER_EXPRESSION_REGEX = r"([^=]+)=([^=]+)(?:\s|$)"


def make_controllers_filter(filter_expression):
    """Build filter func to config's controller.

    If the filter_str is "a=v1,v2,v3 b=v4,v5,v6"
    This will iterate over keys [a,b] to check the value
    inside controller match the values list a in [v1,v2,v3]
    and b in [v4,v5,v6].
    """

    def filter(controller: Controller):
        """Filter controllers."""
        controller_asdict = asdict(controller)
        for key, values in re.findall(
            FILTER_EXPRESSION_REGEX,
            filter_expression,
        ):
            target_val: t.Union[t.List[str], str] = controller_asdict.get(key)
            if key == "tags" and len(set(target_val) & set(values)) <= 0:
                return False
            if isinstance(target_val, str) and asdict(controller).get(key) not in values.split(","):
                return False
        return True

    return filter


def get_filtered_config(filter_expression: str) -> Config:
    config = load_config(CONFIG_PATH, PERSONAL_CONFIG_PATH)
    if filter_expression == "":
        return config
    controller_filter = make_controllers_filter(filter_expression)
    config.controllers = list(filter(controller_filter, config.controllers))
    return config
