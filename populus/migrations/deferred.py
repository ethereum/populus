from __future__ import unicode_literals
import itertools
import functools

from web3.utils.encoding import (
    decode_hex,
)
from web3.utils.types import (
    is_string,
)

from populus.utils.types import (
    is_hex_address,
    is_hex_transaction_hash,
)


class DeferredValue(object):
    chain = None

    def __init__(self, chain, **kwargs):
        self.chain = chain
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(
                    "{0}() received an invalid keyword {1!r}. as_view only "
                    "accepts arguments that are already attributes of the "
                    "class.".format(self.__class__.__name__, key)
                )
            setattr(self, key, value)

    @classmethod
    def defer(cls, **initkwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError(
                    "{0}() received an invalid keyword {1!r}. as_view only "
                    "accepts arguments that are already attributes of the "
                    "class.".format(cls.__name__, key)
                )
        deferred_type = type(cls.__name__, (cls,), initkwargs)
        # without assigning the module here anytime a class is deferred, the
        # deferred class is assigned this module rather than the original
        # module that the class was defined.
        deferred_type.__module__ = cls.__module__
        return deferred_type

    @classmethod
    def deconstruct(cls):
        deferred_kwargs = {
            key: getattr(cls, key)
            for key in dir(cls)
            if (
                not key.startswith('__') and
                not callable(getattr(cls, key)) and
                getattr(cls, key) != getattr(super(cls, cls), key)
            )
        }
        return (
            '.'.join((cls.__module__, cls.__name__, 'defer')),
            tuple(),
            deferred_kwargs,
        )

    def get(self):
        raise NotImplementedError("This method must be implemented by subclasses")


def resolve_if_deferred_value(value, chain):
    if isinstance(value, DeferredValue):
        return value.get()
    elif isinstance(value, type) and issubclass(value, RegistrarValue):
        return value(chain).get()
    else:
        return value


def Resolver(chain):
    return functools.partial(resolve_if_deferred_value, chain=chain)


ALLOWED_VALUE_TYPES = {
    'string'
    'bytes32',
    'address',
    'uint256',
    'int256',
    'bool',
}


class RegistrarValue(DeferredValue):
    key = None
    value_type = None
    value = None

    def exists(self, key):
        return self.chain.registrar.call().exists(key)

    def get(self):
        if not self.exists(self.key):
            raise KeyError(
                "The given key is not set on the registrar: `{0}`".format(self.key)
            )

        caller = self.chain.registrar.call()

        if self.value_type == 'string':
            return caller.getString(self.key)
        elif self.value_type == 'bytes32':
            return caller.get(self.key)
        elif self.value_type == 'address':
            return caller.getAddress(self.key)
        elif self.value_type == 'uint256':
            return caller.getUInt(self.key)
        elif self.value_type == 'int256':
            return caller.getInt(self.key)
        elif self.value_type == 'bool':
            return caller.getBool(self.key)

        raise ValueError("`value_type` must be one of {0}.  Got: {1}".format(
            ', '.join(sorted(ALLOWED_VALUE_TYPES)),
            self.value_type,
        ))

    def set(self, value=None, timeout=120):
        if value is None:
            if self.value is not None:
                value = self.value
            else:
                raise ValueError("No value provided")

        if not is_string(self.key):
            raise ValueError("Invalid key type.  Expected string, got: {0!r}".format(
                type(self.key)
            ))

        transactor = self.chain.registrar.transact()

        if self.value_type == 'string':
            set_txn_hash = transactor.setString(self.key, value)
        elif self.value_type == 'bytes32':
            set_txn_hash = transactor.set(self.key, value)
        elif self.value_type == 'address':
            set_txn_hash = transactor.setAddress(self.key, value)
        elif self.value_type == 'uint256':
            set_txn_hash = transactor.setUInt(self.key, value)
        elif self.value_type == 'int256':
            set_txn_hash = transactor.setInt(self.key, value)
        elif self.value_type == 'bool':
            set_txn_hash = transactor.setBool(self.key, value)
        else:
            raise ValueError("`value_type` must be one of {0}.  Got: {1}".format(
                ', '.join(sorted(ALLOWED_VALUE_TYPES)),
                self.value_type,
            ))

        if timeout is not None:
            self.chain.wait.for_receipt(set_txn_hash, timeout=timeout)

        return set_txn_hash


class Address(RegistrarValue):
    value_type = 'address'


class Bytes32(RegistrarValue):
    value_type = 'bytes32'


class UInt(RegistrarValue):
    value_type = 'uint256'


class Int(RegistrarValue):
    value_type = 'int256'


class String(RegistrarValue):
    value_type = 'string'


class Bool(RegistrarValue):
    value_type = 'bool'


def generate_registrar_value_setters(receipt, prefix=None):
    if prefix is None:
        prefix = []

    if is_string(prefix):
        prefix = [prefix]

    if isinstance(receipt, RegistrarValue):
        raise ValueError("Receipt should not be instantiated at this point")
    elif is_hex_address(receipt):
        # Special case for addresses
        return [
            Address.defer(key='/'.join(prefix), value=receipt)
        ]
    elif is_hex_transaction_hash(receipt):
        # Special case for transaction hashes and addresses.
        return [
            Bytes32.defer(key='/'.join(prefix), value=decode_hex(receipt))
        ]
    elif isinstance(receipt, type) and issubclass(receipt, RegistrarValue):
        return [
            receipt.defer(
                key=receipt.key or '/'.join(prefix),
                value_type=receipt.value_type,
                value=receipt.value,
            )
        ]
    elif isinstance(receipt, dict):
        return list(itertools.chain.from_iterable([
            generate_registrar_value_setters(value, prefix + [key])
            for key, value in receipt.items()
        ]))
    elif isinstance(receipt, (list, tuple)):
        return list(itertools.chain.from_iterable([
            generate_registrar_value_setters(value, prefix + [str(index)])
            for index, value in enumerate(receipt)
        ]))
    else:
        raise ValueError(
            "Invalid type.  Must be one of transaction hash, address, "
            "ReceiptValue, dict, or list"
        )
