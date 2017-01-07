import os
import itertools

from populus.utils.packaging import (
    get_installed_packages_dir,
    find_package_source_files,
    find_installed_package_locations,
    extract_dependency_name_from_base_dir,
    recursive_find_installed_dependency_base_dirs,
)
from populus.utils.filesystem import (
    find_solidity_source_files,
)
from populus.utils.functional import (
    compose,
    cast_return_to_tuple,
)


BUILD_ASSET_DIR = "./build"


def get_build_asset_dir(project_dir):
    build_asset_dir = os.path.join(project_dir, BUILD_ASSET_DIR)
    return build_asset_dir


COMPILED_CONTRACTS_ASSET_FILENAME = './contracts.json'


def get_compiled_contracts_asset_path(build_asset_dir):
    compiled_contracts_asset_path = os.path.join(
        build_asset_dir,
        COMPILED_CONTRACTS_ASSET_FILENAME,
    )
    return compiled_contracts_asset_path


@cast_return_to_tuple
def compute_import_remappings(source_paths, installed_package_locations):
    source_and_remapping_pairs = itertools.product(
        sorted(source_paths),
        sorted(installed_package_locations.items()),
    )
    # TODO: This needs to take into account sub-packages such that any
    # recursively installed packages have their imports appropriately remapped
    # to their nested installed package dirs.
    for import_path, (package_name, package_source_dir) in source_and_remapping_pairs:
        yield "{import_path}:{package_name}={package_source_dir}".format(
            import_path=import_path,
            package_name=package_name,
            package_source_dir=package_source_dir,
        )


def compute_project_compilation_arguments(contracts_source_dir, root_installed_packages_dir):
    project_source_paths = find_solidity_source_files(contracts_source_dir)

    # TODO: this should only compute remappings for solidity files which part
    # of the imports used by the project.  This could be pulled from the AST or
    # by regex.
    project_installed_package_locations = dict(
        (
            extract_dependency_name_from_base_dir(dependency_base_dir),
            dependency_base_dir,
        ) for dependency_base_dir
        in find_installed_package_locations(root_installed_packages_dir)
    )

    project_import_remappings = compute_import_remappings(
        project_source_paths,
        project_installed_package_locations,
    )

    all_installed_dependency_base_dirs = recursive_find_installed_dependency_base_dirs(
        root_installed_packages_dir,
    )

    if all_installed_dependency_base_dirs:
        package_source_paths, package_import_remappings = map(
            compose(itertools.chain.from_iterable, tuple),
            zip(*(
                compute_installed_package_compilation_arguments(dependency_base_dir)
                for dependency_base_dir
                in all_installed_dependency_base_dirs
            )),
        )
    else:
        package_source_paths, package_import_remappings = tuple(), tuple()

    all_import_remappings = itertools.chain(
        project_import_remappings,
        package_import_remappings
    )

    return project_source_paths, package_source_paths, all_import_remappings


def compute_installed_package_compilation_arguments(dependency_base_dir):
    package_source_paths = find_package_source_files(dependency_base_dir)
    package_installed_packages_dir = get_installed_packages_dir(dependency_base_dir)

    if not os.path.exists(package_installed_packages_dir):
        package_installed_package_locations = {}
    else:
        package_installed_package_locations = find_installed_package_locations(
            package_installed_packages_dir,
        )

    package_import_remappings = compute_import_remappings(
        package_source_paths,
        package_installed_package_locations,
    )
    return package_source_paths, package_import_remappings
