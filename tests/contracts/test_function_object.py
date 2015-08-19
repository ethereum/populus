from populus.contracts import (
    Function,
)


def test_abi_signature_no_args():
    func = Function("doit", [])
    assert hex(func.abi_function_signature) == "0x4d536fe3"


def test_abi_signature_single_arg():
    func = Function("register", [("bytes32", "name")])
    assert hex(func.abi_function_signature) == "0xe1fa8e84"


def test_abi_signature_multiple_args():
    func = Function("multiply", [("int256", 'a'), ("int256", 'b')])
    assert hex(func.abi_function_signature) == "0x3c4308a8"


def test_signature_no_args():
    func = Function("doit", [])
    assert str(func) == "doit()"


def test_signature_single_arg():
    func = Function("register", [("bytes32", "name")])
    assert str(func) == "register(bytes32 name)"


def test_signature_multiple_args():
    func = Function("multiply", [("int256", 'a'), ("int256", 'b')])
    assert str(func) == "multiply(int256 a, int256 b)"
