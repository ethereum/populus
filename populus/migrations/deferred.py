


class DeferredValue(object):
    web3 = None

    def __init__(self, web3):
        self.web3 = web3

    @classmethod
    def defer(cls, **init_kwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError(
                    "{0}() received an invalid keyword {1!r}. as_view only "
                    "accepts arguments that are already attributes of the "
                    "class.".format(cls.__name__, key)
                )
        return type(cls.__name__, (cls,), initkwargs)

    def get(self):
        raise NotImplementedError("This method must be implemented by subclasses")


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

    def __init__(self, web3, key=None, value=None, value_type=None):
        if registrar is None:
            raise ValueError("Cannot instantiate RegistrarValue without a registrar")

        self.registrar = get_compiled_registrar_contract(

        if key is not None:
            self.key = key
        if value is not None:
            self.value = value
        if value_type is not None:
            self.value_type = value_type

    def exists(self, key):
        return self.registrar.call().exists(key)

    def get(self):
        if not self.exists(self.key):
            raise KeyError(
                "The given key is not set on the registrar: `{0}`".format(self.key)
            )

        caller = self.registrar.call()

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

        transactor = self.registrar.transact()

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
            wait_for_transaction_receipt(
                web3=self.registrar.web3,
                txn_hash=set_txn_hash,
                timeout=timeout,
            )

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


def resolve_if_registrar_value(value, registrar):
    if isinstance(value, RegistrarValue):
        return value.get()
    elif isinstance(value, type) and issubclass(value, RegistrarValue):
        return value(registrar).get()
    else:
        return value
