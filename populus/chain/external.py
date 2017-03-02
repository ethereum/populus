from .base import (
    BaseChain,
)


class ExternalChain(BaseChain):
    """
    Chain class to represent an externally running blockchain that is not
    locally managed.  This class only houses a pre-configured web3 instance.
    """
    pass
