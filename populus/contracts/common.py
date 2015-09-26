class ContractBound(object):
    _contract = None

    def _bind(self, contract):
        self._contract = contract

    @property
    def contract(self):
        if self._contract is None:
            raise AttributeError("Function not bound to a contract")
        return self._contract
