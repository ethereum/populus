class Registrar(object):
    """
    Abstraction for recording known contracts on a given chain.
    """
    registrar_backends = None

    def __init__(self, chain, registrar_backends):
        self.chain = chain
        self.registrar_backends = registrar_backends

    def set_contract_address(self, contract_name, contract_address):
        return [
            registrar.set_contract_address(contract_name, contract_address)
            for registrar in self.registrar_backends.values()
        ]
