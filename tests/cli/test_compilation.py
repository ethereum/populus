import pytest
from click.testing import CliRunner

from populus.cli import main
from populus.utils.testing import load_contract_fixture


@load_contract_fixture('owned.sol')
@load_contract_fixture('mortal.sol')
@load_contract_fixture('immortal.sol')
def test_compiling(project):
    runner = CliRunner()
    result = runner.invoke(main, ['compile'])

    assert result.exit_code == 0, result.output + str(result.exception)
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'immortal.sol' in result.output
