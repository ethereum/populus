from __future__ import absolute_import

import pprint
import warnings

from cytoolz.dicttoolz import (
    assoc,
)
from cytoolz.functoolz import (
    pipe,
    partial,
)

from semantic_version import (
    Spec,
)

from eth_utils import (
    add_0x_prefix,
    to_dict,
    to_tuple,
    is_string,
)

from solc import (
    compile_files,
    get_solc_version,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.compile import (
    load_json_if_string,
    normalize_contract_metadata,
)
from populus.utils.linking import (
    find_placeholder_locations,
    normalize_placeholder_link_references,
)
from populus.utils.mappings import (
    get_nested_key,
)

from .base import (
    BaseCompilerBackend,
)


def normalize_combined_json_contract_key(key_from_compiler, contract_data):
    if ':' not in key_from_compiler:
        try:
            compilation_target = get_nested_key(
                contract_data,
                'metadata.settings.compilationTarget',
            )
        except KeyError:
            pass
        else:
            if len(compilation_target) != 1:
                raise ValueError('Invalid compilationTarget {}'.format(compilation_target))
            return next(it for it in compilation_target.items())
    source_path, _, name = key_from_compiler.rpartition(':')
    return source_path, name


@to_dict
def normalize_combined_json_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', normalize_contract_metadata(contract_data['metadata'])
    if 'bin' in contract_data:
        yield 'bytecode', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'bytecode_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        yield 'abi', load_json_if_string(contract_data['abi'])
    if 'userdoc' in contract_data:
        yield 'userdoc', load_json_if_string(contract_data['userdoc'])
    if 'devdoc' in contract_data:
        yield 'devdoc', load_json_if_string(contract_data['devdoc'])


@to_tuple
def normalize_compilation_result(compilation_result):
    for key_from_compiler, raw_contract_data in compilation_result.items():
        contract_data = normalize_combined_json_contract_data(raw_contract_data)
        source_path, contract_name = normalize_combined_json_contract_key(
            key_from_compiler,
            contract_data,
        )
        yield pipe(
            contract_data,
            partial(assoc, key='source_path', value=source_path),
            partial(assoc, key='name', value=contract_name),
        )


@to_tuple
def post_process_compiled_contracts(compiled_contracts):
    for contract_data in compiled_contracts:
        bytecode = contract_data.get('bytecode')

        if is_string(bytecode):
            bytecode_placeholder_locations = find_placeholder_locations(bytecode)
            bytecode_link_references = normalize_placeholder_link_references(
                bytecode_placeholder_locations,
                compiled_contracts,
            )
        else:
            bytecode_link_references = tuple()

        bytecode_runtime = contract_data.get('bytecode_runtime')
        if is_string(bytecode_runtime):
            bytecode_runtime_placeholder_locations = find_placeholder_locations(
                bytecode_runtime,
            )
            bytecode_runtime_link_references = normalize_placeholder_link_references(
                bytecode_runtime_placeholder_locations,
                compiled_contracts,
            )
        else:
            bytecode_runtime_link_references = tuple()

        yield pipe(
            contract_data,
            partial(assoc, key='linkrefs', value=bytecode_link_references),
            partial(assoc, key='linkrefs_runtime', value=bytecode_runtime_link_references),
        )


class SolcCombinedJSONBackend(BaseCompilerBackend):
    def __init__(self, *args, **kwargs):
        if get_solc_version() not in Spec('<=0.4.8'):
            raise OSError(
                "The 'SolcCombinedJSONBackend can only be used with solc "
                "versions <=0.4.8.  The SolcStandardJSONBackend should be used "
                "for all versions >=0.4.9"
            )

        warn_msg = 'Support for solc <0.4.11 will be dropped in the next populus release'
        warnings.warn(warn_msg, DeprecationWarning)

        super(SolcCombinedJSONBackend, self).__init__(*args, **kwargs)

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        self.logger.debug("Import remappings: %s", import_remappings)
        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        if 'import_remappings' in self.compiler_settings and import_remappings is not None:
            self.logger.warn("Import remappings setting will be overridden by backend settings")

        try:
            compilation_result = compile_files(
                source_file_paths,
                import_remappings=import_remappings,
                **self.compiler_settings
            )
        except ContractsNotFound:
            return {}

        compiled_contracts = pipe(
            compilation_result,
            normalize_compilation_result,
            post_process_compiled_contracts,
        )

        return compiled_contracts
