pragma solidity ^0.4.0;


contract Registrar {
    address public owner;

    function Registrar() {
        owner = msg.sender;
    }

    modifier onlyowner { if (msg.sender != owner) throw; _; }

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
