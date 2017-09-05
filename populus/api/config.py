
from populus.config.loading import (
    get_user_default_json_config_file_path,
    load_user_config as _load_user_config,

)

from populus.config.helpers import (
    write_config,
)


def load_user_config(user_config_path=None):

    return _load_user_config(user_config_path)


def write_user_config(user_config, user_config_path=None):

    if user_config_path is None:
        user_config_path = get_user_default_json_config_file_path()

    write_config(user_config, user_config_path)
