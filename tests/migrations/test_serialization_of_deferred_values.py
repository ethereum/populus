from __future__ import unicode_literals
import pytest

from populus.migrations.deferred import (
    DeferredValue,
    Address,
)
from populus.migrations.writer import (
    serialize_deconstructable,
)


class Deferred(DeferredValue):
    a = None
    b = None
    c = None


@pytest.mark.parametrize(
    'value,expected_imports,expected_value',
    (
        (
            Address.defer(key='abcd'),
            {'populus.migrations.deferred'},
            """populus.migrations.deferred.Address.defer(
    key='abcd',
)\n""",
        ),
        (
            Deferred.defer(c=4),
            {__name__},
            """{module_part}.Deferred.defer(
    c=4,
)\n""".format(module_part=__name__),
        ),
    ),
)
def test_serialization_of_deferred_values(value, expected_imports, expected_value):
    actual_imports, actual_value = serialize_deconstructable(value)

    assert actual_imports == expected_imports
    assert actual_value == expected_value
