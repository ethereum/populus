from __future__ import absolute_import

import logging
import pprint
import os

from semantic_version import Spec

from eth_utils import (
    add_0x_prefix,
    to_dict,
)

from solc import (
    compile_source,
    compile_files,
    get_solc_version,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.deploy import compute_deploy_order
from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
)
from populus.utils.contract_key_mapping import ContractKeyMapping

from .base import (
    BaseCompilerBackend,
    _load_json_if_string,
    _normalize_contract_metadata,
)


if get_solc_version() in Spec('<0.4.9'):
    def _get_combined_key(key_from_compiler, contract_data):
        metadata = contract_data.get('metadata')
        if metadata is not None:
            targ = metadata.get('settings', {}).get('compilationTarget')
            if targ is not None:
                if len(targ) != 1:
                    raise ValueError('Invalid compilationTarget {}'.format(targ))
                return next(':'.join(it) for it in targ.items())
        return key_from_compiler
else:
    def _get_combined_key(key_from_compiler, _):
        return key_from_compiler


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
            self.logger.warn("Import remappings setting will be overridden by backend settings")

        try:
            compilation_result = compile_files(
                source_file_paths,
                import_remappings=import_remappings,
                **self.compiler_settings,
            )
        except ContractsNotFound:
            return {}

        compiled_contracts = {}
        for key_from_compiler, rawdata in compilation_result.items():
            data = _normalize_combined_json_contract_data(rawdata)
            combined_key = _get_combined_key(key_from_compiler, data)
            path, _, sym = combined_key.rpartition(':')
            compiled_contracts[(path, sym)] = data


        dependency_graph = get_shallow_dependency_graph(
            compiled_contracts,
        )

        deploy_order = compute_deploy_order(dependency_graph)

        for name, contract in compiled_contracts.items():
            deps = get_recursive_contract_dependencies(
                name,
                dependency_graph,
            )
            contract['ordered_dependencies'] = [cid for cid in deploy_order if cid in deps]

        return ContractKeyMapping(compiled_contracts)

