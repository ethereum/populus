import os
import json
import shutil

from web3.utils.string import (
    is_bytes,
)

from populus.utils.filesystem import (
    tempdir,
    ensure_path_exists,
    ensure_file_exists,
    remove_dir_if_exists,
)
from populus.utils.packaging import (
    get_installed_packages_dir,
    get_dependency_base_dir,
    get_release_lockfile_path,
    get_root_identifier_lockfile_path,
    get_translated_identifier_lockfile_path,
    compute_translated_identifier_tree,
    flatten_translated_identifier_tree,
    recursively_resolve_package_data,
)


def install_project_packages(project, package_identifiers):
    """
    1. Recursively resolve all dependencies.
    2. Filter out any dependencies that are already met.
    3. Write dependencies to filesystem

    Maybe:
    - check all chain identifiers are found on the current chain.
    """
    package_backends = project.package_backends

    translated_identifier_tree = compute_translated_identifier_tree(
        package_identifiers,
        package_backends,
    )
    flattened_identifier_tree = flatten_translated_identifier_tree(
        translated_identifier_tree,
    )
    resolved_package_data = tuple(
        recursively_resolve_package_data(package_identifier_lineage, package_backends)
        for package_identifier_lineage
        in flattened_identifier_tree
    )
    # TODO: Filter out dependencies that are already satisfied.
    # TODO: Detect duplicate dependency names
    write_installed_packages(
        project.installed_packages_dir,
        resolved_package_data,
    )

    return resolved_package_data


def write_installed_packages(installed_packages_dir, resolved_package_data):
    with tempdir() as temporary_dir:
        temp_installed_packages_dir = get_installed_packages_dir(temporary_dir)

        if os.path.exists(installed_packages_dir):
            shutil.copytree(installed_packages_dir, temp_installed_packages_dir)
        else:
            ensure_path_exists(temp_installed_packages_dir)

        for package_data in resolved_package_data:
            write_package_files(temp_installed_packages_dir, package_data)
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

        # Write the `root_identifier.lock` lockfile
        root_identifier_lockfile_path = get_root_identifier_lockfile_path(
            temp_install_location,
        )
        with open(root_identifier_lockfile_path, 'w') as root_identifier_lockfile_file:
            root_identifier_lockfile_file.write(package_meta['root_identifier'])

        # Write the `translated_identifier.lock` lockfile
        translated_identifier_lockfile_path = get_translated_identifier_lockfile_path(
            temp_install_location,
        )
        with open(translated_identifier_lockfile_path, 'w') as translated_identifier_lockfile_file:
            translated_identifier_lockfile_file.write(package_meta['translated_identifier'])

        # Now recursively write dependency packages.
        installed_packages_dir_for_dependencies = get_installed_packages_dir(
            dependency_base_dir,
        )
        write_installed_packages(
            installed_packages_dir_for_dependencies,
            package_data['dependencies'],
        )

        # Upon successful writing of all dependencies move the fully installed
        # package dir to the real installed_packages location.
        remove_dir_if_exists(dependency_base_dir)
        shutil.move(temp_install_location, dependency_base_dir)
