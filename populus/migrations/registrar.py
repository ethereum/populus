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


ALLOWED_VALUE_TYPES = {
    'string'
    'bytes32',
    'address',
    'uint256',
    'int256',
    'bool',
}


class RegistrarValue(object):
    registrar = None

    key = None
    value_type = None
    value = None

    @classmethod
    def defer(cls, key=None, value=None, value_type=None):
        proxy_dict = {}

        if key is not None:
            proxy_dict['key'] = key
        if value is not None:
            proxy_dict['value'] = value
        if value_type is not None:
            proxy_dict['value_type'] = value_type

        return type('LazyRegistrarValue', (cls,), proxy_dict)

    def __init__(self, registrar, key=None, value=None, value_type=None):
        self.registrar = registrar

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
