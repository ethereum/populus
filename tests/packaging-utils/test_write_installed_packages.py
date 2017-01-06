import os
import json

from populus import Project

from populus.utils.filesystem import (
    ensure_file_exists,
    ensure_path_exists,
    is_same_path,
)
from populus.utils.packaging import (
    compute_identifier_tree,
    flatten_identifier_tree,
    recursively_resolve_package_data,
    get_dependency_base_dir,
    get_installed_packages_dir,
    get_release_lockfile_path,
    get_build_identifier,
    get_install_identifier,
)

from populus.packages.installation import (
    write_installed_packages,
    write_package_files,
)


def verify_installed_package(installed_packages_dir, package_base_dir, package_data):
    package_meta = package_data['meta']

    expected_package_base_dir = get_dependency_base_dir(
        installed_packages_dir,
        package_meta['dependency_name'],
    )

    assert os.path.exists(package_base_dir)
    assert is_same_path(package_base_dir, expected_package_base_dir)

    for rel_source_path, source_contents in package_data['source_tree'].items():
        source_path = os.path.join(package_base_dir, rel_source_path)
        assert os.path.exists(source_path)
        with open(source_path) as source_file:
            actual_source_contents = source_file.read()
        assert actual_source_contents == source_contents

    build_identifier = get_build_identifier(package_base_dir)
    assert build_identifier == package_meta['build_identifier']

    install_identifier = get_install_identifier(package_base_dir)
    assert install_identifier == package_meta['install_identifier']

    release_lockfile_path = get_release_lockfile_path(package_base_dir)
    with open(release_lockfile_path) as release_lockfile_file:
        release_lockfile = json.load(release_lockfile_file)

    assert release_lockfile == package_data['lockfile']

    package_installed_packages_dir = get_installed_packages_dir(package_base_dir)

    for dependency_package_data in package_data['dependencies']:
        sub_dependency_base_dir = get_dependency_base_dir(
            package_installed_packages_dir,
            dependency_package_data['meta']['dependency_name'],
        )
        verify_installed_package(
            package_installed_packages_dir,
            sub_dependency_base_dir,
            dependency_package_data,
        )


def test_initial_write_of_package_data(temp_dir,
                                       load_example_project,
                                       mock_package_backends):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    package_base_dir = write_package_files(temp_dir, package_data)

    verify_installed_package(temp_dir, package_base_dir, package_data)


def test_write_package_data_with_existing_install(temp_dir,
                                                  load_example_project,
                                                  mock_package_backends):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    package_base_dir = get_dependency_base_dir(temp_dir, 'wallet')

    pre_existing_file_path = os.path.join(package_base_dir, 'test-file.txt')
    ensure_file_exists(pre_existing_file_path)

    pre_existing_dir_path = os.path.join(package_base_dir, 'test-dir')
    ensure_path_exists(pre_existing_dir_path)
    ensure_file_exists(os.path.join(pre_existing_dir_path, 'is-present'))

    write_package_files(temp_dir, package_data)

    assert not os.path.exists(pre_existing_file_path)
    assert not os.path.exists(pre_existing_dir_path)
    assert not os.path.exists(os.path.join(pre_existing_dir_path, 'is-present'))
