import os
from click.testing import CliRunner

from populus.utils.compile import (
    get_contracts_source_dirs,
)

from populus.cli import main


def test_initializing_empty_project(project_dir):
    contracts_source_dirs = get_contracts_source_dirs(project_dir)

    for source_dir in contracts_source_dirs:
        os.rmdir(source_dir)

    expected_paths = (
        os.path.join(project_dir, 'populus.json'),
        os.path.join(project_dir, 'tests'),
        os.path.join(contracts_source_dirs[0], 'Greeter.sol'),
        os.path.join(project_dir, 'tests', 'test_greeter.py'),
    ) + tuple(
        source_dir for source_dir in contracts_source_dirs
    )

    for path in expected_paths:
        assert not os.path.exists(path)

    runner = CliRunner()
    result = runner.invoke(main, ['init'])

    assert result.exit_code == 0, result.output + str(result.exception)
    assert 'Created Example Contract' in result.output

    for path in expected_paths:
        assert os.path.exists(path)
