from populus.migrations import (
    Migration,
    SendTransaction,
    DeployContract,
    RunPython,
    TransactContract,
)


def test_migration_execution(MATH):
    class TestMigration(Migration):
        migration_id = '0001_initial'
        dependencies = []

        operations = [
            DeployContract('Math'),
        ]

        contract_data = {
            'Math': {
                'code': "0x606060405260405160208060318339506080604052518015601e576002565b50600680602b6000396000f3606060405200",
                'code_runtime': "0x606060405200",
                'abi': [
                    {
                        "inputs": [{"name": "shouldThrow", "type": "bool"}],
                        "type": "constructor",
                    },
                ],
            },
        }
    assert False
