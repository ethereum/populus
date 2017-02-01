import os
import glob
import re
from importlib import (
    import_module,
)
try:
    from importlib import invalidate_caches
except ImportError:
    from populus.utils.functional import noop as invalidate_caches

try:
    from importlib import reload
except ImportError:
    pass

from populus.utils.filesystem import (
    get_migrations_dir,
)


VALID_MIGRATION_REGEX = re.compile(
    r'^[0-9]{4}_[_a-zA-Z0-9]+\.py$',
)


def is_valid_migration_filename(filename):
    return bool(VALID_MIGRATION_REGEX.match(filename))


def find_project_migrations(project_dir):
    migrations_dir = get_migrations_dir(project_dir)
    glob_pattern = os.path.join(migrations_dir, '*.py')
    migrations = [
        os.path.relpath(migration_path, project_dir)
        for migration_path
        in glob.glob(glob_pattern)
        if is_valid_migration_filename(os.path.basename(migration_path))
    ]
    return migrations


def load_project_migrations(project_dir):
    migration_file_paths = [
        os.path.relpath(file_path, project_dir)
        for file_path in find_project_migrations(project_dir)
    ]
    migration_module_paths = [
        file_path[:-3].replace(os.sep, '.')
        for file_path in migration_file_paths
    ]

    # we need to both
    invalidate_caches()
    migration_base_paths = set([
        migration_module_path.rpartition('.')[0]
        for migration_module_path in migration_module_paths
    ])

    for migration_base_path in migration_base_paths:
        reload(import_module(migration_base_path))

    migration_modules = [
        reload(import_module(module_path))
        for module_path in migration_module_paths
    ]

    migration_classes = [
        getattr(migration_module, 'Migration')
        for migration_module in migration_modules
    ]
    return migration_classes
