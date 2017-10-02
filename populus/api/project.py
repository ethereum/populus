import os
import shutil

from populus import ASSETS_DIR

from populus.config.helpers import (
    check_if_json_config_file_exists,
)

from populus.utils.filesystem import (
    ensure_path_exists,
)

from populus.project import (
    Project,
)

GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')
GREETER_TEST_PATH = os.path.join(ASSETS_DIR, 'test_greeter.py')


def init_project(project_dir, logger):

    if project_dir is None:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.abspath(project_dir)

    has_json_config = check_if_json_config_file_exists(project_dir)

    if has_json_config:
        logger.info(
            "Found existing `project.json` file.  Not writing default config."
        )

    project = Project(project_dir, create_config_file=True)
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
