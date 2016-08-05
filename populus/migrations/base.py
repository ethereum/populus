from toposort import toposort

from populus.utils.transactions import (
    wait_for_transaction_receipt,
)

from .validation import (
    validate_all_migrations_have_ids,
    validate_migration_id_uniqueness,
    validate_no_self_dependencies,
)
from .registrar import (
    get_compiled_registrar_contract,
    generate_registrar_value_setters,
)


class Migration(object):
    migration_id = None
    dependencies = None
    operations = None
    compiled_contracts = None

    def execute(self, web3, registrar_address):
        if not self.operations:
            raise ValueError("Migrations without operations are not valid.")

        if not self.migration_id:
            raise ValueError("Migrations must have a migration id.")

        registrar = get_compiled_registrar_contract(web3, address=registrar_address)

        migration_registrar_key = "migration/{migration_id}".format(
            migration_id=self.migration_id,
        )

        if registrar.call().exists(migration_registrar_key):
            raise ValueError("This migration has already been run")

        for operation_index, operation in enumerate(self.operations):
            operation_receipt = operation.execute(
                web3=web3,
                compiled_contracts=self.compiled_contracts,
                registrar=registrar,
            )
            if operation_receipt:
                key_prefix = "migration/{migration_id}/operation/{operation_index}".format(
                    migration_id=self.migration_id,
                    operation_index=operation_index,
                )
                registrar_setters = generate_registrar_value_setters(
                    operation_receipt,
                    prefix=key_prefix,
                )
                for setter in registrar_setters:
                    setter.bind(registrar)
                    setter.set()
                    print("setting:", setter.key, setter.value)
        migration_complete_txn = registrar.transact().setBool(migration_registrar_key, True)
        wait_for_transaction_receipt(web3, migration_complete_txn, timeout=30)


def sort_migrations(migration_classes):
    # TODO, this should happen higher up in the call chain.
    validate_all_migrations_have_ids(migration_classes)
    validate_migration_id_uniqueness(migration_classes)
    validate_no_self_dependencies(migration_classes)

    migration_dependency_graph = {
        m.migration_id: set() if m.dependencies is None else set(m.dependencies)
        for m in migration_classes
    }

    migration_classes_by_id = {
        m.migration_id: m for m in migration_classes
    }
    migration_id_order = toposort(migration_dependency_graph)
    migration_order = [
        {migration_classes_by_id[migration_id] for migration_id in execution_set}
        for execution_set in migration_id_order
    ]
    return migration_order
