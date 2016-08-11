from web3.utils.encoding import (
    decode_hex,
)
from populus.migrations import (
    String,
    Address,
    Migration,
    Operation,
)


def test_migrations_store_receipts_on_completion(web3, MATH, registrar):

    class MockOperation(Operation):
        def execute(self, *args, **kwargs):
            return {
                'raw-address': web3.eth.coinbase,
                'raw-txn': '0xebb0f76aa6a6bb8d178ac2354de83d73a728d704bf47d135c188ca7b6d25f2e4',
                'no-key': Address.defer(value=web3.eth.coinbase),
                'with-key': String.defer(key='this-is-a-key', value='this-is-a-string'),
            }


    class TestMigration(Migration):
        migration_id = '0001_initial'
        dependencies = []

        operations = [
            MockOperation(),
        ]

    assert registrar.call().exists('migration/0001_initial') is False
    assert registrar.call().exists('migration/0001_initial/operation/0') is False
    assert registrar.call().exists('migration/0001_initial/operation/0/raw-address') is False
    assert registrar.call().exists('migration/0001_initial/operation/0/raw-txn') is False
    assert registrar.call().exists('migration/0001_initial/operation/0/no-key') is False
    assert registrar.call().exists('this-is-a-key') is False

    migration = TestMigration(web3, registrar)
    migration.execute()

    assert registrar.call().exists('migration/0001_initial') is True
    assert registrar.call().exists('migration/0001_initial/operation/0') is True
    assert registrar.call().exists('migration/0001_initial/operation/0/raw-address') is True
    assert registrar.call().exists('migration/0001_initial/operation/0/raw-txn') is True
    assert registrar.call().exists('migration/0001_initial/operation/0/no-key') is True
    assert registrar.call().exists('this-is-a-key') is True


    assert registrar.call().getBool('migration/0001_initial') is True
    assert registrar.call().getBool('migration/0001_initial/operation/0') is True
    assert registrar.call().getAddress('migration/0001_initial/operation/0/raw-address') == web3.eth.coinbase
    assert registrar.call().get('migration/0001_initial/operation/0/raw-txn') == decode_hex('0xebb0f76aa6a6bb8d178ac2354de83d73a728d704bf47d135c188ca7b6d25f2e4')
    assert registrar.call().getAddress('migration/0001_initial/operation/0/no-key') == web3.eth.coinbase
    assert registrar.call().getString('this-is-a-key') == 'this-is-a-string'
