class ContractError(Exception):
    """
    Base Exception class for errors raised by the Chain contract API.
    """
    pass


class BytecodeMismatchError(ContractError):
    """
    Indicates there is a bytecode mismatch.
    """
    pass


class NoKnownAddress(ContractError):
    """
    Raised when the address for a requested contract is not known.
    """
    pass


class UnknownContract(ContractError):
    """
    Raised when the requested contract name is not found in the compiled
    contracts.
    """
    pass
