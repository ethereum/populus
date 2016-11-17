class ProviderError(Exception):
    """
    Base Exception class for errors raised by the Provider contract API.
    """
    pass


class BytecodeMismatch(ProviderError):
    """
    Indicates there is a bytecode mismatch.
    """
    pass


class NoKnownAddress(ProviderError):
    """
    Raised when the address for a requested contract is not known.
    """
    pass


class UnknownContract(ProviderError):
    """
    Raised when the requested contract name is not found in the compiled
    contracts.
    """
    pass


class InvalidLinkValue(ProviderError):
    """
    Raised when the bytecode length of a link value does not match the required
    length for the necessary link reference, such as a 32-byte value being
    provided for an address sized link reference.
    """
    pass
