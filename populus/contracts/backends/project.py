from __future__ import absolute_import

from populus.utils.contracts import (
    is_project_contract,
)

from .base import (
    BaseContractBackend,
)


class ProjectContractsBackend(BaseContractBackend):
    """
    Provides access to compiled contract assets sources from the project
    `contracts_source_dir`
    """
    is_provider = False
    is_registrar = False
    is_store = True

    #
    # Store API
    #
    def get_contract_identifier(self, contract_name):
        return contract_name

    def get_all_contract_data(self):
        project_contract_data = {
            contract_name: contract_data
            for contract_name, contract_data
            in self.chain.project.compiled_contract_data.items()
            if is_project_contract(self.chain.project.contracts_source_dir, contract_data)
        }
        return project_contract_data
