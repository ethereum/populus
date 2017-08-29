from __future__ import absolute_import

from populus.utils.contracts import (
    is_test_contract,
)

from .base import (
    BaseProjectContractBackend,
)


class TestContractsBackend(BaseProjectContractBackend):
    """
    Provides access to compiled contract assets sources from the project
    `tests_dir`
    """

    #
    # ProviderAPI
    #
    def get_contract_identifier(self, contract_name):
        return contract_name

    def get_all_contract_data(self):
        testing_contract_data = {
            contract_name: contract_data
            for contract_name, contract_data
            in self.provider().project.compiled_contract_data.items()
            if is_test_contract(self.provider().project.tests_dir, contract_data)
        }
        return testing_contract_data
