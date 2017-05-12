from __future__ import absolute_import

import json
import logging
import pprint

from eth_utils import (
    add_0x_prefix,
    is_string,
    to_dict,
)

from solc import (
    compile_files,
    compile_standard,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.deploy import compute_deploy_order
from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
)

from .base import BaseCompilerBackend


def _load_json_if_string(value):
    if is_string(value):
        return json.loads(value)
    else:
        return value


def _get_contract_name(name_from_compiler):
    # TODO: use the source path.
    _, _, contract_name = name_from_compiler.rpartition(':')
    return contract_name


def _normalize_contract_metadata(metadata):
    if not metadata:
        return None
    elif is_string(metadata):
        return json.loads(metadata)
    else:
        raise ValueError("Unknown metadata format '{0}'".format(metadata))


@to_dict
def _normalize_combined_json_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', _normalize_contract_metadata(contract_data['metadata'])
    if 'bin' in contract_data:
        yield 'bytecode', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'bytecode_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        yield 'abi', _load_json_if_string(contract_data['abi'])
    if 'userdoc' in contract_data:
        yield 'userdoc', _load_json_if_string(contract_data['userdoc'])
    if 'devdoc' in contract_data:
        yield 'devdoc', _load_json_if_string(contract_data['devdoc'])


class SolcCombinedJSONBackend(BaseCompilerBackend):
    logger = logging.getLogger('populus.compilation.backends.solc.SolcCombinedJSONBackend')

    def get_compiled_contract_data(self, source_file_paths, import_remappings):
        self.logger.debug("Import remappings: %s", import_remappings)
        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        if 'import_remappings' in self.compiler_settings and import_remappings is not None:
            self.logger.warn("Import remappings setting will by overridden by backend settings")

        try:
            compiled_contracts = compile_files(
                source_file_paths,
                import_remappings=import_remappings,
                **self.compiler_settings,
            )
        except ContractsNotFound:
            return {}

        normalized_compiled_contracts = dict(
            (
                _get_contract_name(name_from_compiler),
                _normalize_combined_json_contract_data(data_from_compiler),
            )
            for name_from_compiler, data_from_compiler
            in compiled_contracts.items()
        )

        dependency_graph = get_shallow_dependency_graph(
            normalized_compiled_contracts,
        )

        deploy_order = compute_deploy_order(dependency_graph)

        for name, contract in normalized_compiled_contracts.items():
            deps = get_recursive_contract_dependencies(
                name,
                dependency_graph,
            )
            contract['ordered_dependencies'] = [cid for cid in deploy_order if cid in deps]

        return {
            'contracts': normalized_compiled_contracts,
            # 'dependency_graph': dependency_graph,
            # 'deploy_order': deploy_order,
        }


class SolcStandardJSONBackend(BaseCompilerBackend):
    logger = logging.getLogger('populus.compilation.backends.solc.SolcStandardJSONBackend')

    def get_compiled_contract_data(self, source_file_paths, import_remappings):
        self.logger.debug("Import remappings: %s", import_remappings)
        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        if 'remappings' in self.compiler_settings and import_remappings is not None:
            self.logger.warn("Import remappings setting will by overridden by backend settings")

        sources = {}
        for sfp in source_file_paths:
            with open(sfp) as f:
                sources[sfp] = { 'content': f.read() }

        std_input = {
            'language': 'Solidity',
            'sources': sources,
            'settings': {
                'remappings': import_remappings
            }
        }
        std_input['settings'].update(self.compiler_settings)


        try:
            compiled_contracts = compile_standard(std_input)
        except ContractsNotFound:
            return {}

        # self.logger.debug("Got contracts %s", json.dumps(compiled_contracts, sort_keys=True, indent=2))

        return compiled_contracts
