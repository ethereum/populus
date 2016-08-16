import itertools

from toposort import toposort

from .deferred import (
    generate_registrar_value_setters,
    Bool,
)


class Migration(object):
    migration_id = None
    dependencies = None
    operations = None
    compiled_contracts = None

    def __init__(self, chain):
        self.chain = chain

    @property
    def registrar(self):
        return self.chain.registrar

    @property
    def web3(self):
        return self.chain.web3

    @property
    def migration_key(self):
        if self.migration_id is None:
            raise ValueError("Migrations must have a `migration_id`")
        key = "migration/{migration_id}".format(
            migration_id=self.migration_id,
        )
        return key

    @property
    def has_been_executed(self):
        if not self.registrar.call().exists(self.migration_key):
            return False
        return self.registrar.call().getBool(self.migration_key)

    def mark_as_executed(self):
        Bool(self.chain, key=self.migration_key, value=True).set()

    def process_operation_receipt(self, operation_key, receipt):
        registrar_setters = generate_registrar_value_setters(
            receipt,
            prefix=operation_key,
        )
        for Setter in registrar_setters:
            print("Key: ", Setter.key)
            Setter(self.chain).set()

        # mark the operation as having been completed.
        Bool(self.chain, key=operation_key, value=True).set()

    def execute(self):
        if self.registrar.call().exists(self.migration_key):
            raise ValueError("This migration has already been run")

        for operation_index, operation in enumerate(self.operations):
            operation_key = "{prefix}/operation/{operation_index}".format(
                prefix=self.migration_key,
                operation_index=operation_index,
            )

            operation_alread_executed = (
                self.registrar.call().exists(operation_key) and
                self.registrar.call().getBool(operation_key)
            )
            if operation_alread_executed:
                # raise or continue?
                raise ValueError("This operation has already been run")

            operation_receipt = operation.execute(
                chain=self.chain,
                compiled_contracts=self.compiled_contracts,
            )

            self.process_operation_receipt(operation_key, operation_receipt)

        self.mark_as_executed()


def sort_migrations(migration_classes, flatten=False):
    migration_dependency_graph = {
        m.migration_id: set() if m.dependencies is None else set(m.dependencies)
        for m in migration_classes
    }

    migration_classes_by_id = {
        m.migration_id: m for m in migration_classes
    }
    migration_id_order = toposort(migration_dependency_graph)
    migration_execution_sets = [
        {migration_classes_by_id[migration_id] for migration_id in execution_set}
        for execution_set in migration_id_order
    ]
    if flatten:
        return list(itertools.chain.from_iterable(migration_execution_sets))
    else:
        return migration_execution_sets


def get_migration_classes_for_execution(migration_classes, chain):
    migration_class_execution_sets = sort_migrations(migration_classes)
    migration_execution_sets = [
        {migration_class(chain) for migration_class in execution_set}
        for execution_set
        in migration_class_execution_sets
    ]

    # For each set of migrations in the sorted order, mark whether all of the
    # migrations in that set have been executed.
    execution_set_statuses = [
        all(m.has_been_executed for m in execution_set)
        for execution_set
        in migration_execution_sets
    ]

    # Now find the first set that has not been fully executed and exclude all
    # of the previous sets which have been fully executed.
    try:
        first_executable_set_idx = execution_set_statuses.index(False)
    except ValueError:
        # All migrations have been executed
        return []

    execution_set_candidates = migration_execution_sets[first_executable_set_idx:]

    # Now we check for an invalid state.  If any migration in any migration set
    # past the first unexecuted set has been executed then something is wrong.
    migrations_that_should_not_be_executed = itertools.chain.from_iterable(
        execution_set_candidates[1:]
    )

    if any(m.has_been_executed for m in migrations_that_should_not_be_executed):
        raise ValueError(
            "Something is wrong.  Migrations that depend on un-executed "
            "migrations have already been executed."
        )

    # Get a flattened list of all of the migration instances that still need to
    # be executed.
    migrations_to_run = [
        migration_instance
        for migration_instance
        in itertools.chain.from_iterable(execution_set_candidates)
        if not migration_instance.has_been_executed
    ]

    return migrations_to_run
