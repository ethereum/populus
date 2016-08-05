import pytest

from populus.migrations import Migration

from populus.migrations.base import (
    sort_migrations,
)


def test_simple_migration_sorting():
    """
    Test a simple linear migration dependency chain.
    A -> B -> C
    """
    class Migration_A(Migration):
        migration_id = "A"

    class Migration_B(Migration):
        migration_id = "B"
        dependencies = ["A"]

    class Migration_C(Migration):
        migration_id = "C"
        dependencies = ["B"]

    migration_execution_order = sort_migrations([
        Migration_A, Migration_B, Migration_C,
    ])

    assert len(migration_execution_order) == 3
    assert migration_execution_order[0] == {Migration_A}
    assert migration_execution_order[1] == {Migration_B}
    assert migration_execution_order[2] == {Migration_C}


def test_multi_dependency_sorting():
    """
    Test a contract with multiple dependencies
    A -> B -> C
    """
    class Migration_A(Migration):
        migration_id = "A"

    class Migration_B(Migration):
        migration_id = "B"
        dependencies = ["A"]

    class Migration_C(Migration):
        migration_id = "C"
        dependencies = ["B"]

    class Migration_D(Migration):
        migration_id = "D"
        dependencies = ["B", "A"]

    migration_execution_order = sort_migrations([
        Migration_A, Migration_B, Migration_C, Migration_D,
    ])

    assert len(migration_execution_order) == 3
    assert migration_execution_order[0] == {Migration_A}
    assert migration_execution_order[1] == {Migration_B}
    assert migration_execution_order[2] == {Migration_C, Migration_D}


def test_circular_dependency_checking():
    """
    Test circular dependencies are handled.
    """
    class Migration_A(Migration):
        migration_id = "A"
        dependencies = ["B"]

    class Migration_B(Migration):
        migration_id = "B"
        dependencies = ["A"]

    with pytest.raises(ValueError):
        sort_migrations([
            Migration_A, Migration_B,
        ])


def test_self_dependency_is_error():
    """
    Test circular dependencies are handled.
    """
    class Migration_A(Migration):
        migration_id = "A"
        dependencies = ["A"]

    with pytest.raises(ValueError):
        sort_migrations([
            Migration_A,
        ])
