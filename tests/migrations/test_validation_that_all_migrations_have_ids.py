import pytest

from populus.migrations import (
    Migration,
)
from populus.migrations.validation import (
    validate_all_migrations_have_ids,
)


def test_with_good_ids():
    class Migration_A(object):
        migration_id = "A"

    class Migration_B(object):
        migration_id = "B"


    validate_all_migrations_have_ids([Migration_A, Migration_B])


@pytest.mark.parametrize(
    "migration_class",
    (
        type('None', (Migration,), {'migration_id': None}),
        type('EmptyString', (Migration,), {'migration_id': ''}),
        type('False', (Migration,), {'migration_id': False}),
        type('Zero', (Migration,), {'migration_id': 0}),
    ),
)
def test_with_migrations_with_falsy_ids(migration_class):
    with pytest.raises(ValueError):
        validate_all_migrations_have_ids([migration_class])
