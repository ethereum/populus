import pytest

from populus.migrations import Migration

from populus.migrations.validation import (
    validate_migration_classes
)


def test_self_dependency_is_error():
    """
    Test circular dependencies are handled.
    """
    class Migration_A(Migration):
        migration_id = "A"
        dependencies = ["A"]

    with pytest.raises(ValueError):
        validate_migration_classes([
            Migration_A,
        ])


def test_null_migration_id_is_error():
    class Migration_A(Migration):
        migration_id = None

    with pytest.raises(ValueError):
        validate_migration_classes([
            Migration_A,
        ])


def test_empty_string_migration_id_is_error():
    class Migration_A(Migration):
        migration_id = ''

    with pytest.raises(ValueError):
        validate_migration_classes([
            Migration_A,
        ])


def test_migration_ids_must_be_unique():
    class Migration_A(Migration):
        migration_id = 'duplicate-id'

    class Migration_B(Migration):
        migration_id = 'duplicate-id'

    with pytest.raises(ValueError):
        validate_migration_classes([
            Migration_A,
            Migration_B,
        ])
