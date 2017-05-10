from populus.utils.contracts import (
    compute_direct_dependency_graph,
)
#
# A -> (B, C)
# B -> null
# C -> (E,)
# D -> (B, E)
# E -> (B,)
#
CONTRACTS = [
    {"name": "A", "direct_dependencies": {"B", "C"}},
    {"name": "B", "direct_dependencies": set()},
    {"name": "C", "direct_dependencies": {"E"}},
    {"name": "D", "direct_dependencies": {"B", "E"}},
    {"name": "E", "direct_dependencies": {"B"}},
]


def test_compute_direct_dependency_graph():
    expected_graph = {
        'A': {'B', 'C'},
        'C': {'E'},
        'D': {'B', 'E'},
        'E': {'B'},
        'B': set(),
    }
    actual_graph = compute_direct_dependency_graph(CONTRACTS)
    assert actual_graph == expected_graph
