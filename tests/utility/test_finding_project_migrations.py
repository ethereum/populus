import os

from populus.utils.filesystem import (
    find_project_migrations,
)


def test_finding_project_migrations(project_dir, write_project_file):
    good_project_migrations = {
        'migrations/0001_initial.py',
        'migrations/0002_something.py',
        'migrations/0003_other.py',
    }

    bad_project_migrations = {
        'migrations/0003_.py',
        'migrations/0003_has-dash.py',
    }

    for file_path in good_project_migrations:
        write_project_file(file_path)

    for file_path in bad_project_migrations:
        write_project_file(file_path)

    found_migrations = find_project_migrations(project_dir)
    assert set(found_migrations) == good_project_migrations
