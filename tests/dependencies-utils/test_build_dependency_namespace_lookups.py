import os

from populus.utils.dependencies import (
    build_dependency_namespace_lookups,
    recursive_find_installed_dependency_base_dirs,
    get_installed_packages_dir,
)
from populus.utils.testing import (
    load_example_package,
)


def test_building_dependency_namespace_lookup_with_no_dependencies():
    namespace_lookups = build_dependency_namespace_lookups(tuple())
    assert not namespace_lookups


@load_example_package('owned')
@load_example_package('standard-token')
def test_building_dependency_namespace_lookup_with_flat_dependencies(project):
    owned_base_dir = os.path.join(project.installed_packages_dir, 'owned')
    standard_token_base_dir = os.path.join(project.installed_packages_dir, 'standard-token')

    dependency_base_dirs = recursive_find_installed_dependency_base_dirs(
        project.installed_packages_dir,
    )
    namespace_lookups = build_dependency_namespace_lookups(dependency_base_dirs)

    assert namespace_lookups[owned_base_dir] == 'owned'
    assert namespace_lookups[standard_token_base_dir] == 'standard-token'


@load_example_package('owned')
@load_example_package('transferable')
@load_example_package('standard-token')
@load_example_package('piper-coin')
def test_building_dependency_namespace_lookup_with_nested_dependencies(project):
    owned_base_dir = os.path.join(project.installed_packages_dir, 'owned')
    transferable_base_dir = os.path.join(project.installed_packages_dir, 'transferable')
    transferable_owned_base_dir = os.path.join(
        get_installed_packages_dir(transferable_base_dir),
        'owned',
    )
    standard_token_base_dir = os.path.join(project.installed_packages_dir, 'standard-token')
    piper_coin_base_dir = os.path.join(project.installed_packages_dir, 'piper-coin')
    piper_coin_standard_token_base_dir = os.path.join(
        get_installed_packages_dir(piper_coin_base_dir),
        'standard-token',
    )

    dependency_base_dirs = recursive_find_installed_dependency_base_dirs(
        project.installed_packages_dir,
    )
    namespace_lookups = build_dependency_namespace_lookups(dependency_base_dirs)

    assert namespace_lookups[owned_base_dir] == 'owned'
    assert namespace_lookups[transferable_base_dir] == 'transferable'
    assert namespace_lookups[standard_token_base_dir] == 'standard-token'
    assert namespace_lookups[piper_coin_base_dir] == 'piper-coin'

    assert namespace_lookups[transferable_owned_base_dir] == 'transferable:owned'
    assert namespace_lookups[piper_coin_standard_token_base_dir] == 'piper-coin:standard-token'
