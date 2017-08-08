import pytest

from populus.contracts.exceptions import (
    BytecodeMismatch,
    NoKnownAddress,
)

from populus.utils.testing import (
    link_bytecode_by_name,
)
from populus.utils.testing import (
    load_example_package,
)


def test_get_contract_factory_with_no_dependencies(chain):
    provider = chain.provider

    MATH = chain.project.compiled_contract_data['Math']
    Math = provider.get_contract_factory('Math')

    assert Math.bytecode == MATH['bytecode']
    assert Math.bytecode_runtime == MATH['bytecode_runtime']


def test_get_contract_factory_with_missing_dependency(chain):
    provider = chain.provider

    with pytest.raises(NoKnownAddress):
        Multiply13 = provider.get_contract_factory('Multiply13')


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

    assert Multiply13.bytecode == expected_bytecode
    assert Multiply13.bytecode_runtime == expected_runtime


def test_get_contract_factory_with_dependency_bytecode_mismatch(chain,
                                                                library_13):
    provider = chain.provider
    registrar = chain.registrar

    # this will not match the expected underlying bytecode for the Library13
    # contract so it will cause a failure.
    registrar.set_contract_address('Library13', '0xd3cda913deb6f67967b99d67acdfa1712c293601')

    with pytest.raises(BytecodeMismatch):
        provider.get_contract_factory('Multiply13')


@pytest.mark.parametrize(
    'contract_type_name',
    ('owned', 'owned:owned'),
)
@load_example_package('owned')
def test_get_contract_factory_from_installed_dependency(chain, contract_type_name):
    provider = chain.provider

    Owned = provider.get_contract_factory(contract_type_name)
    assert Owned.bytecode == chain.project.compiled_contract_data['owned']['bytecode']
