import os
import shutil

from populus import ASSETS_DIR

from populus.config.helpers import (
    check_if_json_config_file_exists,
)

from populus.config import (
    load_user_config,
)
from populus.config.helpers import (
    get_user_default_json_config_file_path,
)

from populus.defaults import (
    USER_JSON_CONFIG_DEFAULTS,
)

from populus.utils.filesystem import (
    ensure_path_exists,
)

from populus.project import (
    Project,
)

GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')
GREETER_TEST_PATH = os.path.join(ASSETS_DIR, 'test_greeter.py')


def init_project(project_dir, user_config_path, logger):

    if project_dir is None:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.abspath(project_dir)

    has_json_config = check_if_json_config_file_exists(project_dir)

    if has_json_config:
        logger.error(
            "Found existing `populus.json` file.  Not writing default config."
        )
        assert False

    if not user_config_path or not os.path.exists(user_config_path):
        default_user_config_asset_path = os.path.join(ASSETS_DIR, USER_JSON_CONFIG_DEFAULTS)
        copy_to = get_user_default_json_config_file_path()
        ensure_path_exists(os.path.dirname(copy_to))
        shutil.copy(
            default_user_config_asset_path,
            copy_to,
        )

    user_config = load_user_config(user_config_path)
    project = Project(project_dir, user_config, create_config_file=True)
    logger.info(
        "Wrote default populus configuration to `./{0}`.".format(
            os.path.relpath(project.config_file_path),
        )
    )

    for source_dir in project.contracts_source_dirs:
        if ensure_path_exists(source_dir):
            logger.info(
                "Created Directory: ./{0}".format(
                    os.path.relpath(source_dir)
                )
            )

    example_contract_path = os.path.join(project.contracts_source_dirs[0], 'Greeter.sol')
    if not os.path.exists(example_contract_path):
        shutil.copy(GREETER_SOURCE_PATH, example_contract_path)
        logger.info("Created Example Contract: ./{0}".format(
            os.path.relpath(example_contract_path)
        ))

    tests_dir = os.path.join(project.project_dir, 'tests')
    if ensure_path_exists(tests_dir):
        logger.info("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_greeter.py')
    if not os.path.exists(example_tests_path):
        shutil.copy(GREETER_TEST_PATH, example_tests_path)
        logger.info("Created Example Tests: ./{0}".format(
            os.path.relpath(example_tests_path)
        ))

    return project
