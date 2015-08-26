from populus.contracts import (
    Function,
)


def test_abi_signature_no_args():
    func = Function("doit", [])
    assert hex(func.abi_function_signature) == "0x4d536fe3"


def test_abi_signature_single_arg():
    func = Function("register", [{'type': 'bytes32', 'name': 'name'}])
    assert hex(func.abi_function_signature) == "0xe1fa8e84"


def test_abi_signature_multiple_args():
    func = Function("multiply", [{'type': 'int256', 'name': 'a'}, {'type': 'int256', 'name': 'b'}])
    assert hex(func.abi_function_signature) == "0x3c4308a8"


def test_signature_no_args():
    func = Function("doit", [])
    assert str(func) == "doit()"


def test_signature_single_arg():
    func = Function("register", [{'type': 'bytes32', 'name': 'name'}])
    assert str(func) == "register(bytes32 name)"


def test_signature_multiple_args():
    func = Function("multiply", [{'type': 'int256', 'name': 'a'}, {'type': 'int256', 'name': 'b'}])
    assert str(func) == "multiply(int256 a, int256 b)"


def test_abi_args_signature(eth_coinbase):
    func = Function("multiply", [{'type': 'address', 'name': 'to'}, {'type': 'uint256', 'name': 'deposit'}])
    args_signature = func.abi_args_signature((eth_coinbase, 12345))
    assert args_signature == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x82\xa9x\xb3\xf5\x96*[\tW\xd9\xee\x9e\xefG.\xe5[B\xf1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0009'


def test_abi_args_signature_with_0x_prefixed_address(eth_coinbase):
    func = Function("multiply", [{'type': 'address', 'name': 'to'}, {'type': 'uint256', 'name': 'deposit'}])
    prefixed_eth_coinbase = '0x' + eth_coinbase
    args_signature = func.abi_args_signature((prefixed_eth_coinbase, 12345))
    assert args_signature == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x82\xa9x\xb3\xf5\x96*[\tW\xd9\xee\x9e\xefG.\xe5[B\xf1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0009'
