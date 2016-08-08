import pytest
from click.testing import CliRunner

from populus.cli import main


CONTRACT_SOURCES = (
    ('contracts/owned.sol', 'contract owned { address owner; function Owned() {owner = msg.sender; }}'),
    ('contracts/mortal.sol', 'import "./owned.sol"; contract mortal is owned { function kill() { suicide(msg.sender); } } contract Immortal is owned { function kill() returns (bool no){ return false; }}'),
)


def test_compiling(project_dir, write_project_file):
    for filename, source in CONTRACT_SOURCES:
        write_project_file(filename, source)

    runner = CliRunner()
    result = runner.invoke(main, ['compile','-s','abi', '-s', 'userdoc'])

    assert result.exit_code == 0, result.output + str(result.exception)
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'mortal' in result.output
    assert 'Immortal' in result.output
