import pytest
import json

from populus.packages.installation import install_packages_to_project

from populus.utils.dependencies import (
    get_dependency_base_dir,
)


@pytest.fixture(autouse=True)
def populate_packages_in_mock_backend(load_example_project):
    load_example_project('owned')
    load_example_project('transferable')
    load_example_project('standard-token')
    load_example_project('piper-coin')
    load_example_project('safe-math-lib')
    load_example_project('escrow')
    load_example_project('wallet')


def test_installing_single_package(temporary_dir,
                                   mock_package_backends,
                                   verify_installed_package):
    installed_packages = install_packages_to_project(
        temporary_dir,
        ['owned'],
        mock_package_backends,
    )

    assert len(installed_packages) == 1

    dependency_base_dir = get_dependency_base_dir(temporary_dir, 'owned')

    verify_installed_package(temporary_dir, dependency_base_dir, installed_packages[0])


def test_installing_multiple_packages(temporary_dir,
                                      mock_package_backends,
                                      verify_installed_package):
    installed_packages = install_packages_to_project(
        temporary_dir,
        ['owned', 'transferable', 'standard-token'],
        mock_package_backends,
    )

    assert len(installed_packages) == 3

    verify_installed_package(
        temporary_dir,
        get_dependency_base_dir(temporary_dir, 'owned'),
        installed_packages[0],
    )
    verify_installed_package(
        temporary_dir,
        get_dependency_base_dir(temporary_dir, 'standard-token'),
        installed_packages[1],
    )
    verify_installed_package(
        temporary_dir,
        get_dependency_base_dir(temporary_dir, 'transferable'),
        installed_packages[2],
    )


def test_installing_project_dependencies(project,
                                         mock_package_backends,
                                         verify_installed_package):
    package_manifest = {
        'package_name': 'test-package',
        'version': '1.0.0',
        'dependencies': {
            'owned': '>=1.0.0',
            'transferable': '>=1.0.0',
            'standard-token': '>=1.0.0',
        }
    }

    with open(project.package_manifest_path, 'w') as package_manifest_file:
        json.dump(package_manifest, package_manifest_file)

    installed_packages = install_packages_to_project(
        project.installed_packages_dir,
        ['.'],
        mock_package_backends,
    )

    assert len(installed_packages) == 3

    verify_installed_package(
        project.installed_packages_dir,
        get_dependency_base_dir(project.installed_packages_dir, 'owned'),
        installed_packages[0],
    )
    verify_installed_package(
        project.installed_packages_dir,
        get_dependency_base_dir(project.installed_packages_dir, 'standard-token'),
        installed_packages[1],
    )
    verify_installed_package(
        project.installed_packages_dir,
        get_dependency_base_dir(project.installed_packages_dir, 'transferable'),
        installed_packages[2],
    )
