import os
import json
import itertools

from .formatting import (
    add_0x_prefix,
)
from .types import (
    is_string,
)
from .packaging import (
    get_installed_packages_dir,
    recursive_find_installed_dependency_base_dirs,
    find_package_source_files,
    get_installed_dependency_locations,
)
from .filesystem import (
    find_solidity_source_files,
)
from .functional import (
    compose,
    cast_return_to_tuple,
    cast_return_to_dict,
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
    project_installed_package_locations = get_installed_dependency_locations(
        root_installed_packages_dir,
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

    package_installed_dependencies = get_installed_dependency_locations(
        package_installed_packages_dir,
    )

    package_import_remappings = compute_import_remappings(
        package_source_paths,
        package_installed_dependencies,
    )
    return package_source_paths, package_import_remappings


@cast_return_to_dict
def normalize_contract_data(contract_data, contract_meta):
    yield 'meta', contract_meta
    if 'bin' in contract_data:
        yield 'code', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'code_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        if is_string(contract_data['abi']):
            yield 'abi', json.loads(contract_data['abi'])
        else:
            yield 'abi', contract_data['abi']
    if 'userdoc' in contract_data:
        if is_string(contract_data['userdoc']):
            yield 'userdoc', json.loads(contract_data['userdoc'])
        else:
            yield 'userdoc', contract_data['userdoc']
    if 'devdoc' in contract_data:
        if is_string(contract_data['devdoc']):
            yield 'devdoc', json.loads(contract_data['devdoc'])
        else:
            yield 'devdoc', contract_data['devdoc']


def process_compiler_output(name_from_compiler, data_from_compiler, contract_meta):
    # TODO: use the source path.
    _, _, contract_name = name_from_compiler.rpartition(':')
    contract_data = normalize_contract_data(data_from_compiler, contract_meta)
    return contract_name, contract_data


@cast_return_to_dict
def get_contract_meta(compiler_kwargs, solc_version):
    yield 'type', 'solc'
    yield 'version', solc_version

    if 'optimize' in compiler_kwargs:
        compiler_meta = {
            key: value
            for key, value
            in compiler_kwargs.items()
            if key in {'optimize', 'optimize_runs'}
        }
        yield 'settings', compiler_meta
