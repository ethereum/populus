import itertools
import functools

from toposort import toposort

from web3.utils.types import is_string

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


def get_contract_data_from_most_recent_deployment_migration(migration_classes,
                                                            contract_name):
    """
    Returns the migration class in which the given contract was deployed.
    """
    from .operations import DeployContract

    sorted_migration_classes = sort_migrations(migration_classes, flatten=True)

    for migration_class in reversed(sorted_migration_classes):
        for operation in reversed(migration_class.operations):
            if not isinstance(operation, DeployContract):
                continue

            if operation.contract_registrar_name is not None:
                op_contract_name = operation.contract_registrar_name
            else:
                op_contract_name = operation.contract_name

            if not is_string(op_contract_name):
                raise TypeError(
                    "Unexpectedly encountered non-string contract name while "
                    "parsing migraton '{0}':  Got {1} of type {2}".format(
                        migration_classes.migraton_id,
                        op_contract_name,
                        type(op_contract_name),
                    )
                )

            if op_contract_name == contract_name:
                return migration_class.compiled_contracts[operation.contract_name]
    else:
        # No migrations found which deploy `contract_name`
        return None


def get_compiled_contracts_from_migrations(migration_classes, chain):
    from .operations import DeployContract

    # Gather the `migration_id` for all of the migrations that have not been
    # run.
    unmigrated_migration_ids = {
        migration.migration_id
        for migration
        in get_migration_classes_for_execution(
            migration_classes,
            chain,
        )
    }

    # Use the set of not-executed migrations to figure out which migrations
    # have already been run.
    migrated_migration_classes = [
        migration_class
        for migration_class
        in migration_classes
        if migration_class.migration_id not in unmigrated_migration_ids
    ]

    # Create a dictionary of all contract data combined from the
    # `compiled_contracts` property of all migration classes that have been
    # executed.
    contract_data_from_migrations = functools.reduce(
        lambda a, b: dict(b, **a),  # merge `a` and `b` with `a` taking priority.
        (m.compiled_contracts for m in reversed(migrated_migration_classes)),
        {},
    )

    # Create a dictionary that contains all known contract data with data from
    # newest migrations being preferred over older migrations and falling back
    # to live project contract data last.
    default_contract_data = dict(
        chain.project.compiled_contracts,
        **contract_data_from_migrations
    )

    # All known contract names from all migations including
    all_contract_names = set(itertools.chain.from_iterable((
        migration_class.compiled_contracts.keys()
        for migration_class in migrated_migration_classes
    ))).union((
        operation.contract_registrar_name or operation.contract_name
        for migration_class in migrated_migration_classes
        for operation in migration_class.operations
        if isinstance(operation, DeployContract)
    ))

    # Now we gather the contract data for each contract from the migration in
    # which it was last deployed.
    contract_data_from_last_deployment = {k: v for k, v in {
        contract_name: get_contract_data_from_most_recent_deployment_migration(
            migrated_migration_classes,
            contract_name,
        ) for contract_name in all_contract_names
    }.items() if v is not None}

    # Merge the contract_data from deployed contracts with the full set of
    # contract data, preferring the contract_data from the deployment
    # migration.  This is our set of contract data.
    compiled_contracts = dict(
        default_contract_data,
        **contract_data_from_last_deployment
    )

    return compiled_contracts
