import os
import pytest


project_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'projects', 'test-01',
)


def test_contracts_fixture(contracts):
    assert contracts.Math
    assert hasattr(contracts.Math, 'add')
    assert hasattr(contracts.Math, 'multiply7')
    assert hasattr(contracts.Math, 'return13')


def test_deployed_contracts_fixture(eth_coinbase, deployed_contracts):
    math = deployed_contracts.Math
    assert math.add.call(11, 12, _from=eth_coinbase) == 23
    assert math.multiply7.call(11, _from=eth_coinbase) == 77
    assert math.return13.call(_from=eth_coinbase) == 13
