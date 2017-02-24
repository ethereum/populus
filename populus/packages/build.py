import os
import itertools

from eth_utils import (
    to_dict,
)

from populus.utils.chains import (
    get_chain_definition,
)
from populus.utils.contracts import (
    is_contract_name,
    EMPTY_BYTECODE_VALUES,
)
from populus.utils.dependencies import (
    extract_build_dependendencies_from_installed_packages,
)
from populus.utils.linking import (
    find_link_references,
)
from populus.utils.mappings import (
    deep_merge_dicts,
)
from populus.utils.packaging import (
    validate_package_manifest,
    persist_package_file,
)


@to_dict
def construct_release_lockfile(project,
                               chain_names,
                               contract_instance_names,
                               contract_type_names):
    if not project.has_package_manifest:
        raise ValueError("No package manifest found in project")

    package_manifest = project.package_manifest
    validate_package_manifest(package_manifest)

    yield 'lockfile_version', '1'
    yield 'package_name', package_manifest['package_name']
    yield 'version', package_manifest['version']

    package_backends = project.package_backends

    source_file_uris = {
        os.path.join('.', file_path): persist_package_file(file_path, package_backends)
        for file_path in project.contract_source_paths
    }
    if source_file_uris:
        yield 'sources', source_file_uris

    deployments = construct_deployments(project, chain_names, contract_instance_names)
    if deployments:
        yield 'deployments', deployments

    package_meta = construct_package_meta_data(package_manifest)
    if package_meta:
        yield 'meta', package_meta

    # TODO: check if there are discrepancies between what is *supposed* to be
    # installed and what is and figure out how to resolve them.
    construct_dependencies = construct_build_dependencies(
        project.installed_packages_dir,
        project.dependencies,
    )
    if construct_dependencies:
        yield 'build_dependencies', construct_dependencies

    contract_types_names_from_deployments = {
        contract_instance['contract_type']
        for deployed_instances in deployments.values()
        for contract_instance in deployed_instances.values()
        if is_contract_name(contract_instance['contract_type'])
    }
    all_contract_type_names = tuple(sorted(set(itertools.chain(
        contract_type_names,
        contract_types_names_from_deployments,
    ))))

    contract_types = construct_contract_types(
        project.compiled_contract_data,
        all_contract_type_names,
    )
    if contract_types:
        yield 'contract_types', contract_types


@to_dict
def construct_deployments(project, chain_names, contract_instance_names):
    for chain_name in chain_names:
        with project.get_chain(chain_name) as chain:
            chain_definition = get_chain_definition(chain.web3)
            provider = chain.provider
            deployed_contract_instances = construct_deployments_object(
                provider,
                contract_instance_names,
            )
            yield chain_definition, deployed_contract_instances


@to_dict
def construct_build_dependencies(installed_packages_dir, project_dependencies):
    installed_dependencies = extract_build_dependendencies_from_installed_packages(
        installed_packages_dir,
    )
    for dependency_name, dependency_identifier in installed_dependencies.items():
        if dependency_name in project_dependencies:
            yield dependency_name, dependency_identifier


@to_dict
def construct_contract_types(compiled_contract_data, contract_type_names):
    for contract_type_name in contract_type_names:
        contract_data = compiled_contract_data[contract_type_name]
        contract_type_object = construct_contract_type_object(
            contract_data,
            contract_type_name,
        )
        yield contract_type_name, contract_type_object


@to_dict
def construct_package_meta_data(package_manifest):
    if 'authors' in package_manifest:
        yield 'authors', package_manifest['authors']
    if 'license' in package_manifest:
        yield 'license', package_manifest['license']
    if 'description' in package_manifest:
        yield 'description', package_manifest['description']
    if 'keywords' in package_manifest:
        yield 'keywords', package_manifest['keywords']
    if 'links' in package_manifest:
        yield 'links', package_manifest['links']


@to_dict
def construct_deployed_contract_instance(provider,
                                         contract_name):
    contract_instance = provider.get_contract(contract_name)
    base_contract_factory = provider.get_base_contract_factory(contract_name)

    yield 'contract_type', contract_instance.populus_meta.contract_type_name
    yield 'address', contract_instance.address

    runtime_bytecode = base_contract_factory.bytecode_runtime
    if runtime_bytecode not in EMPTY_BYTECODE_VALUES:
        yield 'runtime_bytecode', runtime_bytecode

        link_references = find_link_references(
            runtime_bytecode,
            provider.get_all_contract_names(),
        )

        # TODO: scrape all installed package manifests for the names of deployed
        # contracts who's contract class name matches this reference.
        link_dependencies = tuple(
            construct_link_value(provider, link_reference)
            for link_reference
            in link_references
        )

        if link_dependencies:
            yield 'link_dependencies', link_dependencies


@to_dict
def construct_link_value(provider, link_reference):
    yield 'offset', link_reference.offset
    link_reference_contract_instance = provider.get_contract_factory(link_reference.full_name)
    yield 'value', link_reference_contract_instance.populus_meta.contract_type_name


@to_dict
def construct_deployments_object(provider, contract_names_to_include):
    for contract_name in contract_names_to_include:
        deployed_contract_instance = construct_deployed_contract_instance(
            provider,
            contract_name,
        )
        yield contract_name, deployed_contract_instance


@to_dict
def construct_contract_type_object(contract_data,
                                   contract_type_name):
    yield 'contract_name', contract_type_name

    if contract_data.get('bytecode') not in EMPTY_BYTECODE_VALUES:
        yield 'bytecode', contract_data['bytecode']

    if contract_data.get('bytecode_runtime') not in EMPTY_BYTECODE_VALUES:
        yield 'runtime_bytecode', contract_data['bytecode_runtime']

    if 'abi' in contract_data:
        yield 'abi', contract_data['abi']

    if 'userdoc' or 'devdoc' in contract_data:
        natspec = deep_merge_dicts(
            contract_data.get('userdoc', {}),
            contract_data.get('devdoc', {}),
        )
        yield 'natspec', natspec

    if 'runtime_bytecode' in contract_data or 'bytecode' in contract_data:
        yield 'compiler', construct_compiler_object(contract_data['metadata'])


@to_dict
def construct_compiler_object(metadata):
    yield 'type', 'solc'
    yield 'version', metadata['compiler']['version']
    yield 'settings', {
        'optimize': metadata['settings']['optimizer']['enabled'],
        'optimize_runs': metadata['settings']['optimizer']['runs'],
    }
