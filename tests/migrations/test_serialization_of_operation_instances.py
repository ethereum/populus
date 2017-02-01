from __future__ import unicode_literals
import pytest

from populus.migrations import (
    Operation,
    SendTransaction,
    Address,
    TransactContract,
)
from populus.migrations.writer import (
    serialize_deconstructable,
)


@pytest.mark.parametrize(
    'value,expected_imports,expected_value',
    (
        (
            Operation(),
            {'populus.migrations.operations'},
            "populus.migrations.operations.Operation()\n",
        ),
        (
            SendTransaction({}),
            {'populus.migrations.operations'},
            """populus.migrations.operations.SendTransaction(
    transaction={},
)\n""",
        ),
        (
            SendTransaction({
                'to': Address.defer(key='contracts/Math'),
            }, timeout=1234),
            {'populus.migrations.operations', 'populus.migrations.deferred'},
            """populus.migrations.operations.SendTransaction(
    timeout=1234,
    transaction={
        'to': populus.migrations.deferred.Address.defer(
            key='contracts/Math',
        ),
    },
)\n""",
        ),
        (
            TransactContract(
                contract_name='Math',
                method_name='increment',
                arguments=[3],
                contract_address=Address.defer(key='contracts/Math'),
                timeout=1234,
            ),
            {'populus.migrations.operations', 'populus.migrations.deferred'},
            """populus.migrations.operations.TransactContract(
    arguments=[
        3,
    ],
    contract_address=populus.migrations.deferred.Address.defer(
        key='contracts/Math',
    ),
    contract_name='Math',
    method_name='increment',
    timeout=1234,
    transaction={},
)\n""",
        ),
    ),
)
def test_serialization_of_operation_instances(value, expected_imports,
                                              expected_value):
    actual_imports, actual_value = serialize_deconstructable(value)

    assert actual_value == expected_value
    assert actual_imports == expected_imports
