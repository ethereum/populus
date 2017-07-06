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
from populus.utils.string import (
    normalize_class_name,
)


class PopulusContract(Contract):
    populus_meta = None


@to_object('PopulusMeta')
@to_dict
def build_populus_meta(chain, contract_identifier, contract_data):
    yield (
        'is_project_contract',
        is_project_contract(chain.project.contracts_source_dir, contract_data),
    )
    yield (
        'is_test_contract',
        is_test_contract(chain.project.tests_dir, contract_data),
    )
    if isinstance(contract_identifier, tuple):
        _, contract_identifier = contract_identifier
    yield 'contract_type_name', normalize_class_name(contract_identifier).rpartition(':')[2]


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


def construct_contract_factory(chain, contract_identifier, contract_data):
    factory_kwargs = {
        key: contract_data[key]
        for key
        in CONTRACT_FACTORY_FIELDS
        if key in contract_data
    }
    populus_meta = build_populus_meta(chain, contract_identifier, contract_data)
    return chain.web3.eth.contract(
        ContractFactoryClass=PopulusContract,
        populus_meta=populus_meta,
        **factory_kwargs
    )
