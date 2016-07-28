from populus.utils.contracts import (
    get_contract_deploy_order,
)


def test_get_contract_deploy_order():
    dependency_graph = {
        'A': {'B', 'C'},
        'C': {'E'},
        'D': {'B', 'E'},
        'E': {'B'},
        'B': set(),
    }

    # non-deterministic.  Can be deployed in either of these orders.
    expected_deploy_order_a = ['B', 'E', 'D', 'C', 'A']
    expected_deploy_order_b = ['B', 'E', 'C', 'D', 'A']

    actual_deploy_order = get_contract_deploy_order(dependency_graph)

    assert any((
        actual_deploy_order == expected_deploy_order_a,
        actual_deploy_order == expected_deploy_order_b,
    ))
