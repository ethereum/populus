import os

from populus.utils.dependencies import (
    recursive_find_installed_dependency_base_dirs,
    get_installed_packages_dir,
)
from populus.utils.testing import (
    load_example_package,
)


def test_with_no_packages(project):
    base_dirs = recursive_find_installed_dependency_base_dirs(project.installed_packages_dir)
    assert base_dirs == tuple()


@load_example_package('owned')
def test_with_single_package_installed(project):
    assert 'owned' in project.installed_dependency_locations
    base_dirs = recursive_find_installed_dependency_base_dirs(project.installed_packages_dir)
    assert project.installed_dependency_locations['owned'] in base_dirs


@load_example_package('transferable')
def test_with_nested_package_installation(project):
    assert 'transferable' in project.installed_dependency_locations
    assert 'owned' not in project.installed_dependency_locations
    base_dirs = recursive_find_installed_dependency_base_dirs(project.installed_packages_dir)
    assert project.installed_dependency_locations['transferable'] in base_dirs

    owned_base_path = os.path.join(
        get_installed_packages_dir(project.installed_dependency_locations['transferable']),
        'owned',
    )
    assert owned_base_path in base_dirs
