from __future__ import absolute_import

from eth_utils import (
    to_dict,
)

from populus.utils.contracts import (
    is_project_contract,
)

from .base import (
    BaseProjectContractBackend,
)


class ProjectContractsBackend(BaseProjectContractBackend):
    """
    Provides access to compiled contract assets sources from the project
    `contracts_source_dir`
    """

    #
    # Provider API
    #
    def get_contract_identifier(self, contract_name):
        return contract_name

    @to_dict
    def get_all_contract_data(self):
        compiled_contracts = self.provider.project.compiled_contract_data
        for contract_name, contract_data in compiled_contracts.items():
            if is_project_contract(self.provider.project.contracts_source_dir, contract_data):
                yield contract_name, contract_data
