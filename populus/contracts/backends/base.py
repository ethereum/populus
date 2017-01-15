class BaseContractBackend(object):
    chain = None

    def __init__(self, chain, settings):
        self.chain = chain
        self.settings = settings
        self.setup_backend()

    #
    # Meta API
    #
    def is_provider(self):
        raise NotImplementedError("Must be implemented by subclasses")

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
        raise NotImplementedError("Must be implemented by subclasses")

    #
    # Provider API
    #
    def get_contract_address(self, instance_name):
        """
        Returns the known address of the requested contract instance.
        """
        raise NotImplementedError("Must be implemented by subclasses")
