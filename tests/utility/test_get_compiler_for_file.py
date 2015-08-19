import pytest
from populus.utils import get_compiler_for_file

from ethereum._solidity import get_solidity


@pytest.mark.parametrize('filename', ['unknown.txt', 'unknown.bak', 'swap.sol.swp'])
def test_unknown_contract_extensions(filename):
    with pytest.raises(ValueError):
        get_compiler_for_file(filename)


@pytest.mark.skipif(get_solidity() is None, reason="'solc' compiler not available")
def test_solidity_compiler():
    compiler = get_compiler_for_file('Example.sol')
    assert compiler == get_solidity()


@pytest.mark.skipif(get_solidity() is not None, reason="'solc' compiler available")
def test_solidity_compiler_not_available():
    with pytest.raises(ValueError):
        get_compiler_for_file('Example.sol')
