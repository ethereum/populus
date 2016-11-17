from .base import (
    Chain,
)


class ExternalChain(Chain):
    """
    Chain class to represent an externally running blockchain that is not
    locally managed.  This class only houses a pre-configured web3 instance.
    """
    def __enter__(self):
        return self
