from toposort import toposort

from .registrar import (
    get_compiled_registrar_contract,
    generate_registrar_value_setters,
    Bool,
)


class Migration(object):
    migration_id = None
    dependencies = None
    operations = None
    compiled_contracts = None

    registrar_address = None
    web3 = None

    def __init__(self, web3, registrar_address):
        self.web3 = web3
        self.registrar_address = registrar_address

    def execute(self):
        if not self.operations:
            raise ValueError("Migrations without operations are not valid.")

        if not self.migration_id:
            raise ValueError("Migrations must have a migration id.")

        registrar = get_compiled_registrar_contract(
            self.web3,
            address=self.registrar_address,
        )

        migration_key = "migration/{migration_id}".format(
            migration_id=self.migration_id,
        )

        if registrar.call().exists(migration_key):
            raise ValueError("This migration has already been run")

        for operation_index, operation in enumerate(self.operations):
            operation_receipt = operation.execute(
                web3=self.web3,
                compiled_contracts=self.compiled_contracts,
                registrar=registrar,
            )
            if operation_receipt:
                operation_key = "{prefix}/operation/{operation_index}".format(
                    prefix=migration_key,
                    operation_index=operation_index,
                )
                registrar_setters = generate_registrar_value_setters(
                    operation_receipt,
                    prefix=operation_key,
                )
                for Setter in registrar_setters:
                    Setter(registrar).set()

                Bool(registrar, key=operation_key, value=True).set()

        Bool(registrar, key=migration_key, value=True).set()


def sort_migrations(migration_classes):
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
