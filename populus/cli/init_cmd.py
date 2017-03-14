import logging
import os
import shutil

import click

from populus import ASSETS_DIR

from populus.config import (
    load_default_config,
    write_config,
)

from populus.utils.config import (
    get_json_config_file_path,
    check_if_json_config_file_exists,
)
from populus.utils.filesystem import (
    ensure_path_exists,
)

from .main import main


GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')
GREETER_TEST_PATH = os.path.join(ASSETS_DIR, 'test_greeter.py')


@main.command('init')
@click.pass_context
def init_cmd(ctx):
    """
    Generate project layout with an example contract.
    """
    logger = logging.getLogger('populus.cli.init_cmd')
    project = ctx.obj['PROJECT']

    has_json_config = check_if_json_config_file_exists(project.project_dir)

    if has_json_config:
        logger.info(
            "Found existing `populus.json` file.  Not writing default config."
        )
    else:
        json_config_file_path = get_json_config_file_path(project.project_dir)
        default_config = load_default_config()
        write_config(
            project.project_dir,
            default_config,
            json_config_file_path,
        )
        logger.info(
            "Wrote default populus configuration to `./{0}`.".format(
                os.path.relpath(json_config_file_path, project.project_dir),
            )
        )

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

    tests_dir = os.path.join(project.project_dir, 'tests')
    if ensure_path_exists(tests_dir):
        logger.info("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_greeter.py')
    if not os.path.exists(example_tests_path):
        shutil.copy(GREETER_TEST_PATH, example_tests_path)
        logger.info("Created Example Tests: ./{0}".format(
            os.path.relpath(example_tests_path)
        ))
