import anyconfig

from .helpers import (
    get_user_default_json_config_file_path,
)

from .user import (
    UserConfig,
)

from .deploy import (
    DeployConfig,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


def load_user_config(user_config_path=None):

    if user_config_path is None:
        user_config_path = get_user_default_json_config_file_path()

    config = load_config(user_config_path)
    return UserConfig(config)


def load_deploy_config(config_path):

    config = load_config(config_path)
    return DeployConfig(config)


def write_config(project_dir, config, write_path):
    with open(write_path, 'w') as config_file:
        anyconfig.dump(
            dict(config),
            config_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )

    return write_path
