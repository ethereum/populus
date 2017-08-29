
from populus.config.loading import (
    load_user_config as _load_user_config
)

from populus.config.helpers import (
    write_user_config as _write_user_config,
)


def load_user_config(user_config_path=None):

    return _load_user_config(user_config_path)


def write_user_config(user_config, user_config_path=None):

    _write_user_config(user_config, user_config_path)



