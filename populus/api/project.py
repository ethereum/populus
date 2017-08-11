import logging
import os
import shutil

from populus.config.helpers import (
    write_project_config,
)

from populus.config.defaults import (
    load_default_project_config,
)

from populus.config.helpers import (
    check_if_project_json_file_exists,
    write_project_config,
    get_project_json_config_file_path,
)

from populus.utils.filesystem import (
    ensure_path_exists,
)

from populus import ASSETS_DIR, Project
GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')
GREETER_TEST_PATH = os.path.join(ASSETS_DIR, 'test_greeter.py')


def init_project(project_root_dir):

    logger = logging.getLogger('populus.cli.init_cmd')

    default_config = load_default_project_config()
    write_project_config(
            project_root_dir,
            default_config
        )

    logger.info(
            "Wrote default populus configuration to `./{0}`.".format(
                get_project_json_config_file_path(project_root_dir),
            )
        )

    project = Project(project_root_dir)
    project.load_config()

    if ensure_path_exists(project.contracts_source_dir):
        logger.info(
            "Created Directory: ./{0}".format(
                os.path.relpath(project.contracts_source_dir)
            )
        )

    example_contract_path = os.path.join(project.contracts_source_dir, 'Greeter.sol')
    if not os.path.exists(example_contract_path):
        shutil.copy(GREETER_SOURCE_PATH, example_contract_path)
        logger.info("Created Example Contract: ./{0}".format(
            os.path.relpath(example_contract_path)
        ))

    tests_dir = os.path.join(project.project_root_dir, 'tests')
    if ensure_path_exists(tests_dir):
        logger.info("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_greeter.py')
    if not os.path.exists(example_tests_path):
        shutil.copy(GREETER_TEST_PATH, example_tests_path)
        logger.info("Created Example Tests: ./{0}".format(
            os.path.relpath(example_tests_path)
        ))

