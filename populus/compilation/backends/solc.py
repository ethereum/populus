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
)
from solc.exceptions import (
    ContractsNotFound,
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
        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        try:
            compiled_contracts = compile_files(
                source_file_paths,
                import_remappings=import_remappings,
                **self.compiler_settings
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

        return normalized_compiled_contracts


class SolcStandardJSONBackend(BaseCompilerBackend):
    logger = logging.getLogger('populus.compilation.backends.solc.SolcStandardJSONBackend')

    def get_compiled_contract_data(self, source_file_paths, import_remappings):
        raise NotImplementedError("Not yet implemented")
