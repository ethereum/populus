import pytest

from populus.utils.deploy import (
    get_deploy_order,
)


#
# A -> (B, C)
# B -> null
# C -> (E,)
# D -> (B, E)
# E -> (B,)
#
CONTRACTS = {
    "A": {"name": "A", "direct_dependencies": {"B", "C"}},
    "B": {"name": "B", "direct_dependencies": set()},
    "C": {"name": "C", "direct_dependencies": {"E"}},
    "D": {"name": "D", "direct_dependencies": {"B", "E"}},
    "E": {"name": "E", "direct_dependencies": {"B"}},
}


@pytest.mark.parametrize(
    'contracts_to_deploy,expected_deploy_orders',
    (
        (['A'], [
            ['B', 'E', 'C', 'A'],
            ['B', 'E', 'C', 'A'],
        ]),
        (['B'], [['B']]),
        (['C'], [['B', 'E', 'C']]),
        (['D'], [['B', 'E', 'D']]),
        (['E'], [['B', 'E']]),
        (['C', 'D'], [['B', 'E', 'C', 'D'], ['B', 'E', 'D', 'C']]),
        (['A', 'D'], [
            ['B', 'E', 'D', 'C', 'A'],
            ['B', 'E', 'C', 'D', 'A'],
            ['B', 'E', 'C', 'A', 'D'],
        ]),
        (['A', 'B', 'C', 'D', 'E'], [
            ['B', 'E', 'D', 'C', 'A'],
            ['B', 'E', 'C', 'D', 'A'],
            ['B', 'E', 'C', 'A', 'D'],
        ]),
    )
)
def test_get_deploy_order(contracts_to_deploy, expected_deploy_orders):
    actual_deploy_order = list(get_deploy_order(contracts_to_deploy, CONTRACTS))

    assert any([
        actual_deploy_order == expected_deploy_order
        for expected_deploy_order
        in expected_deploy_orders
    ])
