
from populus.migrations import (
    Migration,
    DeployContract,
)
from populus.migrations.migration import (
    get_migration_classes_for_execution,
)

MIGRATION_0001 = ("""
from populus import migrations


class Migration(migrations.Migration):
    migration_id = '0001_initial'
    dependencies = []

    operations = [
        migrations.DeployContract('Math'),
    ]

    compiled_contracts = {
        'Math': {
            'code': '{math_code}',
            'code_runtime': '{math_code_runtime}',
            'abi': '{math_abi},
        },
    }
""")

def test_migrate_cmd(web3, chain, MATH):
    assert False
