import pytest
from populus.compilation import get_compiler_for_file

from populus.solidity import (
    solc,
    is_solc_available,
)


@pytest.mark.parametrize('filename', ['unknown.txt', 'unknown.bak', 'swap.sol.swp'])
def test_unknown_contract_extensions(filename):
    with pytest.raises(ValueError):
        get_compiler_for_file(filename)


@pytest.mark.skipif(is_solc_available() is None, reason="'solc' compiler not available")
def test_solidity_compiler():
    compiler = get_compiler_for_file('Example.sol')
    assert compiler == solc


@pytest.mark.skipif(is_solc_available() is not None, reason="'solc' compiler available")
def test_solidity_compiler_not_available():
    with pytest.raises(ValueError):
        get_compiler_for_file('Example.sol')
