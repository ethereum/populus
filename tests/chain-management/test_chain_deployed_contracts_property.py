import pytest

from populus.utils.linking import (
    link_bytecode_by_name,
)
from populus.chain import (
    NoKnownAddress,
    BytecodeMismatchError,
)
from populus import Project


def test_with_no_deployed_contracts(temp_chain, math, register_address):
    chain = temp_chain

    assert len(chain.deployed_contracts) == 0


def test_with_single_deployed_contract(temp_chain, math, register_address):
    chain = temp_chain

    register_address('Math', math.address)

    assert len(chain.deployed_contracts) == 1
    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21


def test_with_multiple_deployed_contracts(temp_chain,
                                          math,
                                          library_13,
                                          multiply_13,
                                          register_address):
    chain = temp_chain

    register_address('Math', math.address)
    register_address('Library13', library_13.address)
    register_address('Multiply13', multiply_13.address)

    assert len(chain.deployed_contracts) == 3

    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' in chain.deployed_contracts
    assert chain.deployed_contracts.Library13.call().multiply13(3) == 39

    assert 'Multiply13' in chain.deployed_contracts
    assert chain.deployed_contracts.Multiply13.call().multiply13(3) == 39


def test_missing_dependencies_ignored(temp_chain,
                                      math,
                                      library_13,
                                      multiply_13,
                                      register_address):
    chain = temp_chain

    register_address('Math', math.address)
    register_address('Multiply13', multiply_13.address)

    assert len(chain.deployed_contracts) == 1

    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' not in chain.deployed_contracts
    assert 'Multiply13' not in chain.deployed_contracts
