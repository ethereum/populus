import logging
import pprint

from eth_utils import (
    add_0x_prefix,
    to_dict,
)

from solc import (
    compile_standard,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.contract_key_mapping import ContractKeyMapping

from .base import (
    BaseCompilerBackend,
    _load_json_if_string,
    _normalize_contract_metadata,
    add_dependency_info,
)


@to_dict
def _normalize_standard_json_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', _normalize_contract_metadata(contract_data['metadata'])
    if 'evm' in contract_data:
        evm_data = contract_data['evm']
        if 'bytecode' in evm_data:
            yield 'bytecode', add_0x_prefix(evm_data['bytecode'].get('object', ''))
            if 'linkReferences' in evm_data['bytecode']:
                yield 'linkrefs', evm_data['bytecode']['linkReferences']
        if 'deployedBytecode' in evm_data:
            yield 'bytecode_runtime', add_0x_prefix(evm_data['deployedBytecode'].get('object', ''))
            if 'linkReferences' in evm_data['deployedBytecode']:
                yield 'linkrefs_runtime', evm_data['deployedBytecode']['linkReferences']
    if 'abi' in contract_data:
        yield 'abi', _load_json_if_string(contract_data['abi'])
    if 'userdoc' in contract_data:
        yield 'userdoc', _load_json_if_string(contract_data['userdoc'])
    if 'devdoc' in contract_data:
        yield 'devdoc', _load_json_if_string(contract_data['devdoc'])


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
            compilation_result = compile_standard(std_input)
        except ContractsNotFound:
            return {}

        # self.logger.debug("Got contracts %s", json.dumps(compiled_contracts, sort_keys=True, indent=2))
        compiled_contracts = {
            (path, name): _normalize_standard_json_contract_data(contract)
            for path, file_contracts in compilation_result['contracts'].items()
                for name, contract in file_contracts.items()
        }

        add_dependency_info(compiled_contracts)

        return ContractKeyMapping(compiled_contracts)
