import pytest

from populus.contracts.exceptions import (
    NoKnownAddress,
    BytecodeMismatch,
)


def test_getting_contract_with_no_dependencies(chain,
                                               math):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', math.address)

    math = provider.get_contract('Math')
    assert math.call().multiply7(3) == 21


def test_getting_contract_when_not_registered(chain):
    provider = chain.provider

    with pytest.raises(NoKnownAddress):
        provider.get_contract('Math')


def test_getting_contract_with_missing_dependency(chain,
                                                  multiply_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Multiply13', multiply_13.address)

    with pytest.raises(NoKnownAddress):
        provider.get_contract('Multiply13')


def test_getting_contract_with_bytecode_mismatch(chain,
                                                 library_13,
                                                 math):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', library_13.address)

    with pytest.raises(BytecodeMismatch):
        provider.get_contract('Math')


def test_get_contract_with_bytecode_mismatch_on_dependency(chain,
                                                           multiply_13,
                                                           math):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', math.address)

    with pytest.raises(BytecodeMismatch):
        provider.get_contract('Multiply13')


def test_get_contract_with_dependency(chain,
                                      multiply_13,
                                      library_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', library_13.address)

    multiply_13 = provider.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
