import anyconfig

from .user import (
    UserConfig,
)

from .helpers import (
    get_user_default_json_config_file_path,
)


from .validation import (
    load_user_config_schema,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


def load_user_config(user_config_path=None):

    if user_config_path is None:
        user_config_path = get_user_default_json_config_file_path()

    config = load_config(user_config_path)
    schema = load_user_config_schema()
    return UserConfig(config, schema=schema)
