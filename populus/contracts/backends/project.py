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
    is_provider = True
    is_registrar = False

    #
    # Provider API
    #
    def get_contract_identifier(self, contract_name):
        ccd = self.chain.project.compiled_contract_data
        return ccd.normalize_key(contract_name, return_on_no_match=True)

    def get_all_contract_data(self):
        return self.chain.project.compiled_contract_data
