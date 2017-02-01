from web3.utils.formatting import (
    add_0x_prefix,
)

from .functional import (
    cast_return_to_dict,
)


@cast_return_to_dict
def normalize_contract_data(contract_data, contract_meta):
    yield 'meta', contract_meta
    if 'bin' in contract_data:
        yield 'code', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'code_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        yield 'abi', contract_data['abi']
    if 'userdoc' in contract_data:
        yield 'userdoc', contract_data['userdoc']
    if 'devdoc' in contract_data:
        yield 'devdoc', contract_data['devdoc']


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
