import os
import itertools

from populus.utils.linking import (
    find_link_references,
)
from populus.utils.functional import (
    cast_return_to_dict,
)
from populus.utils.chains import (
    get_chain_definition,
)
from populus.utils.contracts import (
    is_contract_name,
)
from populus.utils.packaging import (
    validate_package_manifest,
    persist_package_file,
    extract_build_dependendencies_from_installed_packages,
)


@cast_return_to_dict
def build_release_lockfile(project,
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

    deployments = build_deployments(project, chain_names, contract_instance_names)
    if deployments:
        yield 'deployments', deployments

    package_meta = build_package_meta_data(package_manifest)
    if package_meta:
        yield 'package_meta', package_meta

    # TODO: check if there are discrepancies between what is *supposed* to be
    # installed and what is and figure out how to resolve them.
    build_dependencies = build_build_dependencies(
        project.installed_packages_dir,
        project.dependencies,
    )
    if build_dependencies:
        yield 'build_dependencies', build_dependencies

    contract_types_names_from_deployments = {
        contract_instance['contract_type']
        for deployed_instances in deployments
        for contract_instance in deployed_instances.values()
        if is_contract_name(contract_instance['contract_type'])
    }
    all_contract_type_names = tuple(sorted(set(itertools.chain(
        contract_type_names,
        contract_types_names_from_deployments,
    ))))

    contract_types = build_contract_types(
        project.compiled_contract_data,
        all_contract_type_names,
    )
    if contract_types:
        yield 'contract_types', contract_types


@cast_return_to_dict
def build_deployments(project, chain_names, contract_instance_names):
    for chain_name in chain_names:
        with project.get_chain(chain_name) as chain:
            chain_definition, deployed_contract_instances = construct_deployments_object(
                chain,
                contract_instance_names,
            )
            yield chain_definition, deployed_contract_instances


@cast_return_to_dict
def build_build_dependencies(installed_packages_dir, project_dependencies):
    installed_dependencies = extract_build_dependendencies_from_installed_packages(
        installed_packages_dir,
    )
    for dependency_name, dependency_identifier in installed_dependencies.items():
        if dependency_name in project_dependencies:
            yield dependency_name, dependency_identifier


@cast_return_to_dict
def build_contract_types(compiled_contract_data, contract_type_names):
    for contract_type_name in contract_type_names:
        contract_type_object = construct_contract_type_object(
            compiled_contract_data,
            contract_type_name,
        )
        yield contract_type_name, contract_type_object


@cast_return_to_dict
def build_package_meta_data(package_manifest):
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


EMPTY_BYTECODE_VALUES = {None, "0x"}


def verify_contract_bytecode(chain, contract_name, address):
    contract_data = chain.compiled_contract_data[contract_name]
    provider = chain.contract_provider

    # Check that the contract has bytecode
    if contract_data['code_runtime'] in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Contract instances which contain an address cannot have empty "
            "runtime bytecode"
        )

    ContractFactory = provider.get_contract_factory(contract_name)

    chain_bytecode = chain.web3.eth.getCode(address)

    if chain_bytecode in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "No bytecode found at address: {0}".format(address)
        )
    elif chain_bytecode != ContractFactory.code_runtime:
        raise ValueError(
            "Bytecode found at {0} does not match compiled bytecode:\n"
            " - chain_bytecode: {1}\n"
            " - compiled_bytecode: {2}".format(
                address,
                chain_bytecode,
                ContractFactory.code_runtime,
            )
        )


@cast_return_to_dict
def construct_deployed_contract_instance(provider,
                                         contract_name):
    contract_instance = provider.get_contract(contract_name)
    contract_data = provider.chain.project.compiled_contract_data

    # TODO: handle contract types from dependencies.
    yield 'contract_type', contract_name
    yield 'address', contract_instance.address

    # TODO: populate deploy txn and deploy block

    runtime_bytecode = contract_data['code_runtime']
    if runtime_bytecode not in EMPTY_BYTECODE_VALUES:
        yield 'runtime_bytecode', runtime_bytecode

        link_references = find_link_references(runtime_bytecode, provider.all_contract_names)

        # TODO: scrape all installed package manifests for the names of deployed
        # contracts who's contract class name matches this reference.
        link_dependencies = tuple(
            {'offset': link_reference.offset, 'value': link_reference.full_name}
            for link_reference
            in link_references
        )

        if link_dependencies:
            yield 'link_dependencies', link_dependencies


def construct_deployments_object(chain, contract_names_to_include):
    provider = chain.contract_provider
    chain_definition = get_chain_definition(chain.web3)
    deployment_instances = {
        contract_name: construct_deployed_contract_instance(provider, contract_name)
        for contract_name
        in contract_names_to_include
    }
    return chain_definition, deployment_instances


@cast_return_to_dict
def construct_contract_type_object(compiled_contract_data,
                                   contract_type_name,
                                   contract_type_alias=None):
    if contract_type_alias:
        yield 'contract_name', contract_type_alias
    else:
        yield 'contract_name', contract_type_name

    contract_data = compiled_contract_data[contract_type_name]

    if contract_data.get('code') not in EMPTY_BYTECODE_VALUES:
        yield 'bytecode', contract_data['code']

    if contract_data.get('code_runtime') not in EMPTY_BYTECODE_VALUES:
        yield 'runtime_bytecode', contract_data['code_runtime']

    if contract_data.get('abi'):
        yield 'abi', contract_data['abi']

    if 'userdoc' or 'devdoc' in contract_data:
        # TODO: this needs to be a deep merge.
        natspec = dict(itertools.chain(
            contract_data.get('userdoc', {}).items(),
            contract_data.get('devdoc', {}).items(),
        ))
        yield 'natspec', natspec

    if 'runtime_bytecode' in contract_data or 'bytecode' in contract_data:
        compiler_info = {
            'type': 'solc',
            'version': contract_data['meta']['compilerVersion'],
            'settings': {
                'optimize': True,
            },
        }
        yield 'compiler', compiler_info
