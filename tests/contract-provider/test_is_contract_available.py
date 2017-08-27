import pytest

from populus import Project


def test_contract_availability_with_no_dependencies(chain, registrar, provider, math):

    registrar.set_contract_address('Math', math.address)

    is_available = provider.is_contract_available('Math')
    assert is_available is True


def test_contract_availability_when_not_registered(chain, provider):

    is_available = provider.is_contract_available('Math')
    assert is_available is False


def test_contract_availability_with_missing_dependency(chain,
                                                       registrar,
                                                       provider,
                                                       multiply_13):

    registrar.set_contract_address('Multiply13', multiply_13.address)

    is_available = provider.is_contract_available('Multiply13')
    assert is_available is False


def test_contract_availability_with_bytecode_mismatch(chain,
                                                      registrar,
                                                      provider,
                                                      library_13):

    registrar.set_contract_address('Math', library_13.address)

    is_available = provider.is_contract_available('Math')
    assert is_available is False


def test_contract_availability_with_bytecode_mismatch_on_dependency(chain,
                                                                    registrar,
                                                                    provider,
                                                                    multiply_13,
                                                                    math):

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', math.address)

    is_available = provider.is_contract_available('Multiply13')
    assert is_available is False


def test_contract_availability_with_dependency(chain,
                                               registrar,
                                               provider,
                                               multiply_13,
                                               library_13):

    registrar.set_contract_address('Multiply13', multiply_13.address)
    registrar.set_contract_address('Library13', library_13.address)

    is_available = provider.is_contract_available('Multiply13')
    assert is_available is True
