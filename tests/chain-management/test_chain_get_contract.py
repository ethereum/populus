import pytest

from populus.chain import (
    NoKnownAddress,
    BytecodeMismatchError,
)


def test_getting_contract_with_no_dependencies(temp_chain,
                                               math,
                                               register_address):
    chain = temp_chain

    register_address('Math', math.address)

    math = chain.get_contract('Math')
    assert math.call().multiply7(3) == 21


def test_getting_contract_when_not_registered(temp_chain):
    chain = temp_chain

    with pytest.raises(NoKnownAddress):
        chain.get_contract('Math')


def test_getting_contract_with_missing_dependency(temp_chain,
                                                  multiply_13,
                                                  register_address):
    chain = temp_chain

    register_address('Multiply13', multiply_13.address)

    with pytest.raises(NoKnownAddress):
        chain.get_contract('Multiply13')


def test_getting_contract_with_bytecode_mismatch(temp_chain,
                                                 library_13,
                                                 math,
                                                 register_address):
    chain = temp_chain

    register_address('Math', library_13.address)

    with pytest.raises(BytecodeMismatchError):
        chain.get_contract('Math')


def test_get_contract_skipping_bytecode_validation(temp_chain,
                                                   library_13,
                                                   math,
                                                   register_address):
    chain = temp_chain

    register_address('Math', library_13.address)

    math = chain.get_contract('Math', validate_bytecode=False)


def test_get_contract_with_bytecode_mismatch_on_dependency(temp_chain,
                                                           multiply_13,
                                                           math,
                                                           register_address):
    chain = temp_chain

    register_address('Multiply13', multiply_13.address)
    register_address('Library13', math.address)

    with pytest.raises(BytecodeMismatchError):
        chain.get_contract('Multiply13')


def test_get_contract_with_dependency(temp_chain,
                                      multiply_13,
                                      library_13,
                                      register_address):
    chain = temp_chain

    register_address('Multiply13', multiply_13.address)
    register_address('Library13', library_13.address)

    multiply_13 = chain.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39


def test_get_contract_with_declared_dependency(temp_chain,
                                               multiply_13,
                                               library_13,
                                               register_address):
    chain = temp_chain

    register_address('Multiply13', multiply_13.address)

    multiply_13 = chain.get_contract(
        'Multiply13',
        link_dependencies={'Library13': library_13.address},
    )
    assert multiply_13.call().multiply13(3) == 39
