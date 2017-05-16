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

from .base import (
    BaseCompilerBackend,
    _load_json_if_string,
    _normalize_contract_metadata,
)


@to_dict
def _normalize_standard_json_contract_data(contract_data):
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
