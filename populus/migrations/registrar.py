import itertools

from solc import compile_source

from web3.utils.encoding import (
    decode_hex,
)

from populus.utils.transactions import (
    wait_for_transaction_receipt,
)
from populus.utils.types import (
    is_string,
    is_hex_address,
    is_hex_transaction_hash,
)

from .operations import DeployContract


REGISTRAR_SOURCE = """contract Registrar {
    address public owner;

    function Registrar() {
        owner = msg.sender;
    }

    modifier onlyowner { if (msg.sender != owner) throw; _ }

    function transferOwner(address newOwner) public onlyowner {
        owner = newOwner;
    }

    Registrar public parent;

    function setParent(address parentAddress) public onlyowner {
        parent = Registrar(parentAddress);
    }

    mapping (bytes32 => bytes32) records;
    mapping (bytes32 => string) stringRecords;
    mapping (bytes32 => bool) recordExists;


    function set(string key, bytes32 value) public onlyowner {
        // Compute the fixed length key
        bytes32 _key = sha3(key);

        // Do not allow overwriting keys
        if (recordExists[_key]) throw;

        // Set the value
        records[_key] = value;
        recordExists[_key] = true;
    }

    function get(string key) constant returns (bytes32) {
        // Compute the fixed length key
        bytes32 _key = sha3(key);

        if (!recordExists[_key]) {
            if (address(parent) == 0x0) {
                // Do return unset keys
                throw;
            } else {
                // Delegate to the parent.
                return parent.get(key);
            }
        }

        return records[_key];
    }

    function exists(string key) constant returns (bool) {
        // Compute the fixed length key
        bytes32 _key = sha3(key);

        return recordExists[_key];
    }

    function setAddress(string key, address value) public onlyowner {
        set(key, bytes32(value));
    }

    function getAddress(string key) constant returns (address) {
        return address(get(key));
    }

    function setUInt(string key, uint value) public onlyowner {
        set(key, bytes32(value));
    }

    function getUInt(string key) constant returns (uint) {
        return uint(get(key));
    }

    function setInt(string key, int value) public onlyowner {
        set(key, bytes32(value));
    }

    function getInt(string key) constant returns (int) {
        return int(get(key));
    }

    function setBool(string key, bool value) public onlyowner {
        if (value) {
            set(key, bytes32(0x1));
        } else {
            set(key, bytes32(0x0));
        }
    }

    function getBool(string key) constant returns (bool) {
        return get(key) != bytes32(0x0);
    }

    function setString(string key, string value) public onlyowner {
        bytes32 valueHash = sha3(value);
        set(key, valueHash);
        stringRecords[valueHash] = value;
    }

    function getString(string key) public returns (string) {
        bytes32 valueHash = get(key);
        return stringRecords[valueHash];
    }
}
"""


def get_compiled_registrar_contract(web3, address=None):
    compiled_contracts = compile_source(REGISTRAR_SOURCE)
    contract_data = compiled_contracts['Registrar']
    return web3.eth.contract(
        address=address,
        abi=contract_data['abi'],
        code=contract_data['code'],
        code_runtime=contract_data['code_runtime'],
        source=REGISTRAR_SOURCE,
    )


class DeployRegistrar(DeployContract):
    def __init__(self, **kwargs):
        super(DeployRegistrar, self).__init__(
            contract_name="Registrar",
            **kwargs
        )

    def execute(self, web3, **kwargs):
        kwargs.pop('compiled_contracts', None)
        compiled_contracts = compile_source(REGISTRAR_SOURCE)
        return super(DeployRegistrar, self).execute(
            web3=web3,
            compiled_contracts=compiled_contracts,
            **kwargs
        )


ALLOWED_VALUE_TYPES = {
    'string'
    'bytes32',
    'address',
    'uint256',
    'int256',
    'bool',
}


class RegistrarValue(object):
    key = None
    value_type = None
    value = None

    registrar = None

    def __init__(self, key, value_type, value=None):
        self.key = key
        self.value_type = value_type
        self.value = value

    def bind(self, registrar):
        self.registrar = registrar

    def exists(self, key):
        if not self.registrar:
            raise ValueError("Must bind a registrar before calling this method")
        return self.registrar.call().exists(key)

    def get(self):
        if self.value is None:
            if not self.registrar:
                raise ValueError("Must bind a registrar before calling this method")

            if not self.exists(self.key):
                raise KeyError(
                    "The given key is not set on the registrar: `{0}`".format(self.key)
                )

            caller = self.registrar.call()

            if self.value_type == 'string':
                self.value = caller.getString(self.key)
            elif self.value_type == 'bytes32':
                self.value = caller.get(self.key)
            elif self.value_type == 'address':
                self.value = caller.getAddress(self.key)
            elif self.value_type == 'uint256':
                self.value = caller.getUInt(self.key)
            elif self.value_type == 'int256':
                self.value = caller.getInt(self.key)
            elif self.value_type == 'bool':
                self.value = caller.getBool(self.key)
            else:
                raise ValueError("`value_type` must be one of {0}.  Got: {1}".format(
                    ', '.join(sorted(ALLOWED_VALUE_TYPES)),
                    self.value_type,
                ))
        return self.value

    def set(self, value=None, timeout=30):
        if value is None and self.value is None:
            raise ValueError("Must either provide value during constructor or call to `set`")
        elif value is not None:
            self.value = value

        if not self.registrar:
            raise ValueError("Must bind a registrar before calling this method")

        if self.exists(self.key):
            raise KeyError(
                "The given key is already set on the registrar: `{0}`".format(self.key)
            )

        transactor = self.registrar.transact()

        if self.value_type == 'string':
            set_txn_hash = transactor.setString(self.key, self.value)
        elif self.value_type == 'bytes32':
            set_txn_hash = transactor.set(self.key, self.value)
        elif self.value_type == 'address':
            set_txn_hash = transactor.setAddress(self.key, self.value)
        elif self.value_type == 'uint256':
            set_txn_hash = transactor.setUInt(self.key, self.value)
        elif self.value_type == 'int256':
            set_txn_hash = transactor.setInt(self.key, self.value)
        elif self.value_type == 'bool':
            set_txn_hash = transactor.setBool(self.key, self.value)
        else:
            raise ValueError("`value_type` must be one of {0}.  Got: {1}".format(
                ', '.join(sorted(ALLOWED_VALUE_TYPES)),
                self.value_type,
            ))

        if timeout is not None:
            wait_for_transaction_receipt(self.registrar.web3, set_txn_hash, timeout)

        return set_txn_hash


class Address(RegistrarValue):
    def __init__(self, key, value=None):
        super(Address, self).__init__(key, 'address', value)


class Bytes32(RegistrarValue):
    def __init__(self, key, value=None):
        super(Bytes32, self).__init__(key, 'bytes32', value)


class UInt(RegistrarValue):
    def __init__(self, key, value=None):
        super(UInt, self).__init__(key, 'uint256', value)


class Int(RegistrarValue):
    def __init__(self, key, value=None):
        super(Int, self).__init__(key, 'int256', value)


class String(RegistrarValue):
    def __init__(self, key, value=None):
        super(String, self).__init__(key, 'string', value)


class Bool(RegistrarValue):
    def __init__(self, key, value=None):
        super(Bool, self).__init__(key, 'bool', value)


class ReceiptValue(object):
    def __init__(self, value, value_type):
        if value_type not in ALLOWED_VALUE_TYPES:
            raise ValueError("`value_type` must be one of {0}.  Got: {1}".format(
                ', '.join(sorted(ALLOWED_VALUE_TYPES)),
                value_type,
            ))
        self.value = value
        self.value_type = value_type


def generate_registrar_value_setters(receipt, prefix=None):
    if prefix is None:
        prefix = []

    if is_string(prefix):
        prefix = [prefix]

    if is_hex_address(receipt):
        # Special case for addresses
        return [
            Address(key='/'.join(prefix), value=receipt)
        ]
    if is_hex_transaction_hash(receipt):
        # Special case for transaction hashes and addresses.
        return [
            Bytes32(key='/'.join(prefix), value=decode_hex(receipt))
        ]
    elif isinstance(receipt, ReceiptValue):
        return [RegistrarValue(
            key='/'.join(prefix),
            value_type=receipt.value_type,
            value=receipt.value,
        )]
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
        raise ValueError("Invalid type.  Must be one of ReceiptValue, dict, or list")
