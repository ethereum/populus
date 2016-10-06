import os
import json

from flaky import flaky

from click.testing import CliRunner

from populus.project import Project
from populus import migrations
from populus.migrations.registrar import (
    get_registrar,
)
from populus.migrations.writer import (
    write_migration,
)

from populus.cli import main


@flaky
def test_migrate_cmd(project_dir, write_project_file, MATH):
    class MigrationA(migrations.Migration):
        migration_id = '0001_deploy_math'
        dependencies = []

        operations = [
            migrations.DeployContract('Math'),
        ]

        compiled_contracts = {
            'Math': MATH,
        }

    class MigrationB(migrations.Migration):
        migration_id = '0002_increment'
        dependencies = ['0001_deploy_math']

        operations = [
            migrations.TransactContract(
                contract_name='Math',
                method_name='increment',
                arguments=[3],
                contract_address=migrations.Address.defer(key='contract/Math'),
                timeout=30,
            ),
        ]

        compiled_contracts = {
            'Math': MATH,
        }


    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file('migrations/__init__.py')

    migration_0001_path = os.path.join(
        project_dir, 'migrations', '0001_deploy_math.py',
    )
    with open(migration_0001_path, 'w') as migration_0001:
        write_migration(migration_0001, MigrationA)

    migration_0002_path = os.path.join(
        project_dir, 'migrations', '0002_increment.py',
    )
    with open(migration_0002_path, 'w') as migration_0002:
        write_migration(migration_0002, MigrationB)

    write_project_file('populus.ini', '[chain:local_a]')

    project = Project()

    # sanity
    assert len(project.migrations) == 2

    with project.get_chain('local_a') as chain:
        chain.wait.for_unlock(chain.web3.eth.coinbase, timeout=30)
        project.config.set('chain:local_a', 'deploy_from', chain.web3.eth.coinbase)
        RegistrarFactory = get_registrar(web3=chain.web3)
        deploy_transaction_hash = RegistrarFactory.deploy()
        registrar_address = chain.wait.for_contract_address(deploy_transaction_hash, timeout=60)
        project.config.set('chain:local_a', 'registrar', registrar_address)
        project.write_config()

    runner = CliRunner()
    result = runner.invoke(main, ['migrate', 'local_a'])

    assert result.exit_code == 0, result.output + str(result.exception)

    with project.get_chain('local_a') as chain:
        registrar = chain.registrar
        math_address = registrar.call().getAddress('contract/Math')
        Math = chain.contract_factories.Math(address=math_address)
        assert Math.call().counter() == 3
