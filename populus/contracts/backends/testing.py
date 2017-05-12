from __future__ import absolute_import

from populus.utils.contracts import (
    is_test_contract,
)

from .base import (
    BaseContractBackend,
)


class TestContractsBackend(BaseContractBackend):
    """
    Provides access to compiled contract assets sources from the project
    `tests_dir`
    """
    is_provider = False
    is_registrar = False
    is_store = True

    #
    # ProviderAPI
    #
    def get_contract_identifier(self, contract_name):
        return contract_name

    def get_all_contract_data(self):
        testing_contract_data = {
            contract_name: contract_data
            for contract_name, contract_data
            in self.chain.project.compiled_contract_data['contracts'].items()
            if is_test_contract(self.chain.project.contracts_source_dir, contract_data)
        }
        return testing_contract_data
