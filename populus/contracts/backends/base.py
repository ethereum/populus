class BaseContractBackend(object):
    chain = None

    def __init__(self, chain, config):
        self.chain = chain
        self.config = config
        self.setup_backend()

    #
    # Meta API
    #
    @property
    def is_provider(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def is_registrar(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def setup_backend(self):
        """
        Hook for subclasses to do backend initialization without having to
        override the `__init__` method.
        """
        pass

    #
    # Registrar API
    #
    def set_contract_address(self, instance_name, address):
        """
        Returns the address for the contract instance in the registrar.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    #
    # Provider API
    #
    def get_contract_address(self, instance_name):
        """
        Returns the known address of the requested contract instance.
        """
        raise NotImplementedError("Must be implemented by subclasses")
