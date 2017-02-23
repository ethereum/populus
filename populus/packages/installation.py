import os
import json
import shutil

from eth_utils import (
    is_bytes,
    to_tuple,
)

from populus.utils.dependencies import (
    get_build_identifier_lockfile_path,
    get_dependency_base_dir,
    get_install_identifier_lockfile_path,
    get_installed_packages_dir,
    get_release_lockfile_path,
)
from populus.utils.filesystem import (
    ensure_file_exists,
    ensure_path_exists,
    is_under_path,
    remove_dir_if_exists,
    tempdir,
)
from populus.utils.packaging import (
    compute_identifier_tree,
    construct_dependency_identifier,
    flatten_identifier_tree,
    recursively_resolve_package_data,
)


def install_packages_to_project(installed_packages_dir, package_identifiers, package_backends):
    """
    1. Recursively resolve all dependencies.
    2. Filter out any dependencies that are already met.
    3. Write dependencies to filesystem

    Maybe:
    - check all chain identifiers are found on the current chain.
    """
    identifier_tree = compute_identifier_tree(
        package_identifiers,
        package_backends,
    )
    flattened_identifier_tree = flatten_identifier_tree(
        identifier_tree,
    )
    package_data_to_install = tuple(
        recursively_resolve_package_data(package_identifier_lineage, package_backends)
        for package_identifier_lineage
        in flattened_identifier_tree
    )
    # TODO: Filter out dependencies that are already satisfied.
    # TODO: Detect duplicate dependency names
    installed_packages = write_installed_packages(
        installed_packages_dir,
        package_data_to_install,
    )

    return installed_packages


@to_tuple
def write_installed_packages(installed_packages_dir, package_data_to_install):
    with tempdir() as temporary_dir:
        temp_installed_packages_dir = get_installed_packages_dir(temporary_dir)

        if os.path.exists(installed_packages_dir):
            shutil.copytree(installed_packages_dir, temp_installed_packages_dir)
        else:
            ensure_path_exists(temp_installed_packages_dir)

        sorted_package_data_to_install = sorted(
            package_data_to_install,
            key=lambda pd: pd['meta']['dependency_name']
        )

        for package_data in sorted_package_data_to_install:
            write_package_files(temp_installed_packages_dir, package_data)
            yield package_data
        else:
            # Upon successful writing of all dependencies, move
            remove_dir_if_exists(installed_packages_dir)
            shutil.move(temp_installed_packages_dir, installed_packages_dir)


def write_package_files(installed_packages_dir, package_data):
    with tempdir() as temporary_dir:
        package_meta = package_data['meta']

        dependency_name = package_meta['dependency_name']

        # Compute the location the package should be installed to.
        dependency_base_dir = get_dependency_base_dir(
            installed_packages_dir,
            dependency_name,
        )

        # Setup a temporary location to write files.
        temp_install_location = get_dependency_base_dir(
            temporary_dir,
            dependency_name,
        )
        ensure_path_exists(temp_install_location)

        # Write the package source tree.
        package_source_tree = package_data['source_tree']
        for rel_source_path, source_content in package_source_tree.items():
            source_path = os.path.join(temp_install_location, rel_source_path)
            if not is_under_path(temp_install_location, source_path):
                raise ValueError(
                    "Package is attempting to write files outside of the "
                    "installation directory.\n'{0}'".format(rel_source_path)
                )
            ensure_file_exists(source_path)
            mode = 'wb' if is_bytes(source_content) else 'w'
            with open(source_path, mode) as source_file:
                source_file.write(source_content)

        # Write the `lock.json` lockfile
        if package_data['lockfile'] is not None:
            lockfile_path = get_release_lockfile_path(
                temp_install_location,
            )
            with open(lockfile_path, 'w') as lockfile_file:
                lockfile_file.write(json.dumps(
                    package_data['lockfile'],
                    indent=2,
                    sort_keys=True,
                ))

        # Write the `build_identifier.lock` lockfile
        build_identifier_lockfile_path = get_build_identifier_lockfile_path(
            temp_install_location,
        )
        with open(build_identifier_lockfile_path, 'w') as build_identifier_lockfile_file:
            build_identifier_lockfile_file.write(package_meta['build_identifier'])

        # Write the `install_identifier.lock` lockfile
        install_identifier_lockfile_path = get_install_identifier_lockfile_path(
            temp_install_location,
        )
        with open(install_identifier_lockfile_path, 'w') as install_identifier_lockfile_file:
            install_identifier_lockfile_file.write(package_meta['install_identifier'])

        # Now recursively write dependency packages.
        installed_packages_dir_for_dependencies = get_installed_packages_dir(
            temp_install_location,
        )
        write_installed_packages(
            installed_packages_dir_for_dependencies,
            package_data['dependencies'],
        )

        # Upon successful writing of all dependencies move the fully installed
        # package dir to the real installed_packages location.
        remove_dir_if_exists(dependency_base_dir)
        shutil.move(temp_install_location, dependency_base_dir)
    return dependency_base_dir


def update_project_dependencies(project, installed_dependencies):
    if not project.has_package_manifest:
        with open(project.package_manifest_path, 'w') as package_manifest_file:
            json.dump({}, package_manifest_file)

    package_manifest = project.package_manifest
    package_manifest.setdefault('dependencies', {})

    for package_data in installed_dependencies:
        package_meta = package_data['meta']

        dependency_name = package_meta['dependency_name']
        install_identifier = package_meta['install_identifier']
        build_identifier = package_meta['build_identifier']

        dependency_identifier = construct_dependency_identifier(
            dependency_name,
            install_identifier,
            build_identifier,
        )

        package_manifest['dependencies'][dependency_name] = dependency_identifier

    with open(project.package_manifest_path, 'w') as package_manifest_file:
        json.dump(
            package_manifest,
            package_manifest_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )
