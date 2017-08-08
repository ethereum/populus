import pprint

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
)

from solc import (
    get_solc_version,
    compile_standard,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.compile import (
    load_json_if_string,
    normalize_contract_metadata,
)
from populus.utils.linking import (
    normalize_standard_json_link_references,
)

from .base import (
    BaseCompilerBackend,
)


@to_dict
def build_standard_input_sources(source_file_paths):
    for file_path in source_file_paths:
        with open(file_path) as source_file:
            yield file_path, {'content': source_file.read()}


@to_dict
def normalize_standard_json_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', normalize_contract_metadata(contract_data['metadata'])
    if 'evm' in contract_data:
        evm_data = contract_data['evm']
        if 'bytecode' in evm_data:
            yield 'bytecode', add_0x_prefix(evm_data['bytecode'].get('object', ''))
            if 'linkReferences' in evm_data['bytecode']:
                yield 'linkrefs', normalize_standard_json_link_references(
                    evm_data['bytecode']['linkReferences'],
                )
        if 'deployedBytecode' in evm_data:
            yield 'bytecode_runtime', add_0x_prefix(evm_data['deployedBytecode'].get('object', ''))
            if 'linkReferences' in evm_data['deployedBytecode']:
                yield 'linkrefs_runtime', normalize_standard_json_link_references(
                    evm_data['deployedBytecode']['linkReferences'],
                )
    if 'abi' in contract_data:
        yield 'abi', load_json_if_string(contract_data['abi'])
    if 'userdoc' in contract_data:
        yield 'userdoc', load_json_if_string(contract_data['userdoc'])
    if 'devdoc' in contract_data:
        yield 'devdoc', load_json_if_string(contract_data['devdoc'])


@to_tuple
def normalize_compilation_result(compilation_result):
    """
    Take the result from the --standard-json compilation and flatten it into an
    interable of contract data dictionaries.
    """
    for source_path, file_contracts in compilation_result['contracts'].items():
        for contract_name, raw_contract_data in file_contracts.items():
            contract_data = normalize_standard_json_contract_data(raw_contract_data)
            yield pipe(
                contract_data,
                partial(assoc, key='source_path', value=source_path),
                partial(assoc, key='name', value=contract_name),
            )


class SolcStandardJSONBackend(BaseCompilerBackend):
    def __init__(self, *args, **kwargs):
        if get_solc_version() not in Spec('>=0.4.11'):
            raise OSError(
                "The 'SolcStandardJSONBackend can only be used with solc "
                "versions >=0.4.11.  The SolcCombinedJSONBackend should be used "
                "for all versions <=0.4.8"
            )
        super(SolcStandardJSONBackend, self).__init__(*args, **kwargs)

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        self.logger.debug("Import remappings: %s", import_remappings)
        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        if 'remappings' in self.compiler_settings and import_remappings is not None:
            self.logger.warn("Import remappings setting will by overridden by backend settings")

        sources = build_standard_input_sources(source_file_paths)

        std_input = {
            'language': 'Solidity',
            'sources': sources,
            'settings': {
                'remappings': import_remappings
            }
        }

        # solc command line options as passed to solc_wrapper()
        # https://github.com/pipermerriam/py-solc/blob/3a6de359dc31375df46418e6ffd7f45ab9567287/solc/wrapper.py#L20
        command_line_options = self.compiler_settings.get("command_line_options", {})

        # Get Solidity Input Description settings section
        # http://solidity.readthedocs.io/en/develop/using-the-compiler.html#input-description
        std_input_settings = self.compiler_settings.get("stdin", {})
        std_input['settings'].update(std_input_settings)

        self.logger.debug("std_input sections: %s", std_input.keys())
        self.logger.debug("Input Description JSON settings are: %s", std_input["settings"])
        self.logger.debug("Command line options are: %s", command_line_options)
        try:
            compilation_result = compile_standard(std_input, **command_line_options)
        except ContractsNotFound:
            return {}

        compiled_contracts = normalize_compilation_result(compilation_result)
        return compiled_contracts
