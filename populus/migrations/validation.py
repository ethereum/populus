import collections


def validate_all_migrations_have_ids(migration_classes):
    migration_ids = [m.migration_id for m in migration_classes]

    if not all(migration_ids):
        raise ValueError("All migrations must have an id")


def validate_migration_id_uniqueness(migration_classes):
    id_counts = collections.Counter((m.migration_id for m in migration_classes))

    duplicate_ids = [
        migration_id for migration_id, count in id_counts.items() if count > 1
    ]
    if duplicate_ids:
        raise ValueError("All migrations must have unique ids")


def validate_no_self_dependencies(migration_classes):
    migration_dependency_graph = {
        m.migration_id: set() if m.dependencies is None else set(m.dependencies)
        for m in migration_classes
    }

    has_self_dependencies = [
        migration_id
        for migration_id, migration_dependencies
        in migration_dependency_graph.items()
        if migration_id in migration_dependencies
    ]

    if has_self_dependencies:
        raise ValueError("Migrations cannot depend on themselves")


def validate_migration_classes(migration_classes):
    validate_all_migrations_have_ids(migration_classes)
    validate_migration_id_uniqueness(migration_classes)
    validate_no_self_dependencies(migration_classes)
