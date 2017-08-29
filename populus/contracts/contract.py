from __future__ import absolute_import

from eth_utils import (
    to_dict,
)

from web3.contract import (
    Contract,
)

from populus.utils.contracts import (
    is_project_contract,
    is_test_contract,
)
from populus.utils.functional import (
    to_object,
)


class PopulusContract(Contract):
    populus_meta = None


@to_object('PopulusMeta')
@to_dict
def build_populus_meta(project, contract_data):
    yield (
        'is_project_contract',
        is_project_contract(project.contracts_source_dir, contract_data),
    )
    yield (
        'is_test_contract',
        is_test_contract(project.tests_dir, contract_data),
    )
    yield 'contract_type_name', contract_data['name']
    yield 'source_path', contract_data['source_path']


CONTRACT_FACTORY_FIELDS = {
    'abi',
    'asm',
    'ast',
    'bytecode',
    'bytecode_runtime',
    'clone_bin',
    'dev_doc',
    'interface',
    'metadata',
    'opcodes',
    'src_map',
    'src_map_runtime',
    'user_doc',
}


def construct_project_contract_factory(project, web3, contract_identifier, contract_data):
    factory_kwargs = {
        key: contract_data[key]
        for key
        in CONTRACT_FACTORY_FIELDS
        if key in contract_data
    }
    populus_meta = build_populus_meta(project, contract_data)
    return web3.eth.contract(
        ContractFactoryClass=PopulusContract,
        populus_meta=populus_meta,
        **factory_kwargs
    )
