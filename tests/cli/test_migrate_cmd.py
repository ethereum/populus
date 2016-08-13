import json

from click.testing import CliRunner

from populus.project import Project
from populus.migrations.registrar import (
    get_compiled_registrar_contract,
)
from populus.utils.transactions import (
    get_contract_address_from_txn,
    wait_for_unlock,
)
from populus.cli import main


MIGRATION_0001 = ("""
import json
from populus import migrations


class Migration(migrations.Migration):
    migration_id = '0001_deploy_math'
    dependencies = []

    operations = [
        migrations.DeployContract('Math'),
    ]

    compiled_contracts = {{
        'Math': {{
            'code': '{code}',
            'code_runtime': '{code_runtime}',
            'abi': json.loads('{abi}'),
            'source': None,
        }},
    }}
""")


MIGRATION_0002 = ("""
import json
from populus import migrations


class Migration(migrations.Migration):
    migration_id = '0002_increment'
    dependencies = []

    operations = [
        migrations.TransactContract(
            contract_name='Math',
            method_name='increment',
            arguments=[3],
            contract_address=migrations.Address.defer(key='contract/Math'),
            timeout=30,
        ),
    ]

    compiled_contracts = {{
        'Math': {{
            'code': '{code}',
            'code_runtime': '{code_runtime}',
            'abi': json.loads('{abi}'),
            'source': None,
        }},
    }}
""")


def test_migrate_cmd(project_dir, write_project_file, MATH):
    math_code = MATH['code']
    math_runtime = MATH['code_runtime']
    math_abi = json.dumps(MATH['abi'])

    write_project_file('migrations/0001_deploy_math.py', MIGRATION_0001.format(
        abi=math_abi,
        code=math_code,
        code_runtime=math_runtime,
    ))
    write_project_file('migrations/0002_increment.py', MIGRATION_0002.format(
        abi=math_abi,
        code=math_code,
        code_runtime=math_runtime,
    ))
    write_project_file('populus.ini', '[chain:local_a]')

    project = Project()

    # sanity
    assert len(project.migrations) == 2

    with project.get_chain('local_a') as chain:
        wait_for_unlock(chain.web3, chain.web3.eth.coinbase, 30)
        project.config.set('chain:local_a', 'deploy_from', chain.web3.eth.coinbase)
        RegistrarFactory = get_compiled_registrar_contract(web3=chain.web3)
        deploy_transaction_hash = RegistrarFactory.deploy()
        registrar_address = get_contract_address_from_txn(
            chain.web3, deploy_transaction_hash, 60,
        )
        project.config.set('chain:local_a', 'registrar', registrar_address)
        project.write_config()

    runner = CliRunner()
    result = runner.invoke(main, ['migrate', '--chain', 'local_a'])

    with project.get_chain('local_a') as chain:
        registrar = chain.registrar
        import pdb; pdb.set_trace()

    assert result.exit_code == 0, result.output + str(result.exception)

    with project.get_chain('local_a') as chain:
        registrar = chain.registrar
        math_address = registrar.call().getAddress('contract/Math')
        Math = chain.contract_factories.Math(address=math_address)
        assert Math.call().counter() == 3
