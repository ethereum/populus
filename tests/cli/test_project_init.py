import os
import shutil
import pytest
from click.testing import CliRunner

from populus.cli import main
from populus.defaults import PROJECT_JSON_CONFIG_FILENAME

def test_initializing_empty_project(project):

    os.remove(
        os.path.join(project.project_root_dir, PROJECT_JSON_CONFIG_FILENAME)
    )
    shutil.rmtree(project.contracts_source_dir)
    shutil.rmtree(project.tests_dir)
    shutil.rmtree(project.build_asset_dir)

    expected_paths = (
        os.path.join(project.project_root_dir, PROJECT_JSON_CONFIG_FILENAME),
        os.path.join(project.contracts_source_dir, 'Greeter.sol'),
        os.path.join(project.tests_dir, 'test_greeter.py'),
        project.build_asset_dir

    )

    runner = CliRunner()
    result = runner.invoke(main, ['init'])

    assert result.exit_code == 0, result.output + str(result.exception)
    assert 'Created Example Contract' in result.output

    for path in expected_paths:
        assert os.path.exists(path)
