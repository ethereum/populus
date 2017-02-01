import pytest

from populus.migrations import (
    Migration,
)
from populus.migrations.validation import (
    validate_migration_id_uniqueness,
)


def test_with_no_dups():
    class Migration_A(object):
        migration_id = "A"

    class Migration_B(object):
        migration_id = "B"


    validate_migration_id_uniqueness([Migration_A, Migration_B])


def test_with_with_duplicates():
    class Migration_A(object):
        migration_id = "A"

    class Migration_B(object):
        migration_id = "B"

    class Migration_Duplicate(object):
        migration_id = "B"


    with pytest.raises(ValueError):
        validate_migration_id_uniqueness([
            Migration_A, Migration_B, Migration_Duplicate
        ])
