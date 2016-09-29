from solc import compile_source

from populus.utils.contracts import (
    link_bytecode,
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


def get_contract_from_registrar(chain,
                                contract_name,
                                contract_factory,
                                link_dependencies=None):
    if link_dependencies is None:
        link_dependencies = {}

    web3 = chain.web3
    registrar = chain.registrar
    registrar_key = 'contract/{name}'.format(name=contract_name)

    if not registrar.call().exists(registrar_key):
        return None

    contract_address = registrar.call().getAddress(registrar_key)

    expected_runtime = link_bytecode(
        contract_factory.code_runtime,
        **link_dependencies
    )
    actual_runtime = web3.eth.getCode(contract_address)

    # If the runtime doesn't match then don't choose it.
    if actual_runtime != expected_runtime:
        return None

    return contract_factory(address=contract_address)
