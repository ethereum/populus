from .base import BaseContractBackend


class InstalledPackagesContractBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    def is_registrar(self):
        return False

    def is_provider(self):
        return True

    def get_contract_address(self, contract_name):
        raise NotImplementedError('TODO: implement this function')
