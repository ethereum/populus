import pytest

from populus.contracts.exceptions import (
    NoKnownAddress,
    BytecodeMismatch,
)


def test_getting_contract_with_no_dependencies(provider,
                                               registrar,
                                               math):

    registrar.set_contract_address('Math', math.address)

    math = provider.get_contract('Math')
    assert math.call().multiply7(3) == 21


def test_latest_deployed_version_is_used(provider):

    math_1, deploy_txn_1 = provider.deploy_contract('Math')
    math_2, deploy_txn_2 = provider.deploy_contract('Math')

    assert math_1.address != math_2.address

    math = provider.get_contract('Math')
    assert math.call().multiply7(3) == 21

    assert math.address == math_2.address


def test_getting_contract_when_not_registered(provider):

    with pytest.raises(NoKnownAddress):
        provider.get_contract('Math')


def test_getting_contract_with_missing_dependency(chain,
                                                  registrar,
                                                  provider,
                                                  multiply_13):

    registrar.set_contract_address('Multiply13', multiply_13.address)

    with pytest.raises(NoKnownAddress):
        provider.get_contract('Multiply13')


def test_getting_contract_with_bytecode_mismatch(chain,
                                                 registrar,
                                                 provider,
                                                 library_13,
                                                 math):

    registrar.set_contract_address('Math', library_13.address)

    with pytest.raises(BytecodeMismatch):
        provider.get_contract('Math')


def test_get_contract_with_bytecode_mismatch_on_dependency(chain,
                                                           registrar,
                                                           provider,
                                                           multiply_13,
                                                           math):

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', math.address)

    with pytest.raises(BytecodeMismatch):
        provider.get_contract('Multiply13')


def test_get_contract_with_dependency(chain,
                                      registrar,
                                      provider,
                                      multiply_13,
                                      library_13):

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', library_13.address)

    multiply_13 = provider.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
