import pytest

from populus.contracts.exceptions import (
    BytecodeMismatch,
    NoKnownAddress,
)
from populus.utils.hexadecimal import hexbytes_to_hexstr

from populus.utils.testing import (
    link_bytecode_by_name,
)


def test_get_contract_factory_with_no_dependencies(chain):
    provider = chain.provider

    MATH = chain.project.compiled_contract_data['Math']
    Math = provider.get_contract_factory('Math')

    assert hexbytes_to_hexstr(Math.bytecode) == MATH['bytecode']
    assert hexbytes_to_hexstr(Math.bytecode_runtime) == MATH['bytecode_runtime']


def test_get_contract_factory_with_missing_dependency(chain):
    provider = chain.provider

    with pytest.raises(NoKnownAddress):
        provider.get_contract_factory('Multiply13')


def test_get_contract_factory_with_dependency(chain,
                                              library_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Library13', library_13.address)

    MULTIPLY_13 = chain.project.compiled_contract_data['Multiply13']
    Multiply13 = provider.get_contract_factory('Multiply13')

    expected_bytecode = link_bytecode_by_name(
        MULTIPLY_13['bytecode'],
        MULTIPLY_13['linkrefs'],
        Library13=library_13.address,
    )
    expected_runtime = link_bytecode_by_name(
        MULTIPLY_13['bytecode_runtime'],
        MULTIPLY_13['linkrefs_runtime'],
        Library13=library_13.address,
    )
    assert hexbytes_to_hexstr(Multiply13.bytecode) == expected_bytecode
    assert hexbytes_to_hexstr(Multiply13.bytecode_runtime) == expected_runtime


def test_get_contract_factory_with_dependency_bytecode_mismatch(chain,
                                                                library_13):
    provider = chain.provider
    registrar = chain.registrar

    # this will not match the expected underlying bytecode for the Library13
    # contract so it will cause a failure.
    registrar.set_contract_address('Library13', '0xd3CdA913deB6f67967B99D67aCDFa1712C293601')

    with pytest.raises(BytecodeMismatch):
        provider.get_contract_factory('Multiply13')
