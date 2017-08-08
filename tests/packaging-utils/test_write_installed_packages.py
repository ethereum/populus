import os
import json

from populus import Project

from populus.packages.installation import (
    write_installed_packages,
    write_package_files,
)

from populus.utils.dependencies import (
    get_dependency_base_dir,
)
from populus.utils.filesystem import (
    ensure_file_exists,
    ensure_path_exists,
    is_same_path,
)
from populus.utils.packaging import (
    compute_identifier_tree,
    flatten_identifier_tree,
    recursively_resolve_package_data,
)


def test_initial_write_of_package_data(temporary_dir,
                                       load_example_project,
                                       mock_package_backends,
                                       verify_installed_package):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    package_base_dir = write_package_files(temporary_dir, package_data)

    verify_installed_package(temporary_dir, package_base_dir, package_data)


def test_write_package_data_with_existing_install(temporary_dir,
                                                  load_example_project,
                                                  mock_package_backends,
                                                  verify_installed_package):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    package_base_dir = get_dependency_base_dir(temporary_dir, 'wallet')

    pre_existing_file_path = os.path.join(package_base_dir, 'test-file.txt')
    ensure_file_exists(pre_existing_file_path)

    pre_existing_dir_path = os.path.join(package_base_dir, 'test-dir')
    ensure_path_exists(pre_existing_dir_path)
    ensure_file_exists(os.path.join(pre_existing_dir_path, 'is-present'))

    write_package_files(temporary_dir, package_data)

    assert not os.path.exists(pre_existing_file_path)
    assert not os.path.exists(pre_existing_dir_path)
    assert not os.path.exists(os.path.join(pre_existing_dir_path, 'is-present'))


def test_write_project_packages_with_no_installed_packages(temporary_dir,
                                                           load_example_project,
                                                           mock_package_backends,
                                                           verify_installed_package):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')

    lineages = flatten_identifier_tree(
        compute_identifier_tree(['wallet'],mock_package_backends),
    )
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    pre_existing_file_path = os.path.join(temporary_dir, 'test-file.txt')
    ensure_file_exists(pre_existing_file_path)

    pre_existing_dir_path = os.path.join(temporary_dir, 'test-dir')
    ensure_path_exists(pre_existing_dir_path)
    ensure_file_exists(os.path.join(pre_existing_dir_path, 'is-present'))

    write_installed_packages(
        temporary_dir,
        [package_data],

    )

    assert os.path.exists(pre_existing_file_path)
    assert os.path.exists(pre_existing_dir_path)
    assert os.path.exists(os.path.join(pre_existing_dir_path, 'is-present'))

    wallet_package_base_dir = get_dependency_base_dir(temporary_dir, 'wallet')
    verify_installed_package(
        temporary_dir,
        wallet_package_base_dir,
        package_data,
    )


def test_write_project_packages_with_existing_install(temporary_dir,
                                                      load_example_project,
                                                      mock_package_backends,
                                                      verify_installed_package):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')

    project = Project()

    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(
        lineages[0],
        mock_package_backends,
    )

    pre_existing_file_path = os.path.join(temporary_dir, 'test-file.txt')
    ensure_file_exists(pre_existing_file_path)

    pre_existing_dir_path = os.path.join(temporary_dir, 'test-dir')
    ensure_path_exists(pre_existing_dir_path)
    ensure_file_exists(os.path.join(pre_existing_dir_path, 'is-present'))

    wallet_package_base_dir = get_dependency_base_dir(temporary_dir, 'wallet')
    ensure_file_exists(os.path.join(wallet_package_base_dir, 'another-test-file.txt'))

    write_installed_packages(
        temporary_dir,
        [package_data],

    )

    assert os.path.exists(pre_existing_file_path)
    assert os.path.exists(pre_existing_dir_path)
    assert os.path.exists(os.path.join(pre_existing_dir_path, 'is-present'))
    assert not os.path.exists(os.path.join(wallet_package_base_dir, 'another-test-file.txt'))

    verify_installed_package(
        temporary_dir,
        wallet_package_base_dir,
        package_data,
    )
