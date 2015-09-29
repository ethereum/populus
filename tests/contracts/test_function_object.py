from populus.contracts import (
    Function,
)


def test_abi_signature_no_args():
    func = Function("doit", [])
    assert hex(func.abi_signature) == "0x4d536fe3"


def test_abi_signature_single_arg():
    func = Function("register", [{'type': 'bytes32', 'name': 'name'}])
    assert hex(func.abi_signature) == "0xe1fa8e84"


def test_abi_signature_multiple_args():
    func = Function("multiply", [{'type': 'int256', 'name': 'a'}, {'type': 'int256', 'name': 'b'}])
    assert hex(func.abi_signature) == "0x3c4308a8"


def test_signature_no_args():
    func = Function("doit", [])
    assert str(func) == "doit()"


def test_signature_single_arg():
    func = Function("register", [{'type': 'bytes32', 'name': 'name'}])
    assert str(func) == "register(bytes32 name)"


def test_signature_multiple_args():
    func = Function("multiply", [{'type': 'int256', 'name': 'a'}, {'type': 'int256', 'name': 'b'}])
    assert str(func) == "multiply(int256 a, int256 b)"


def test_abi_args_signature():
    func = Function("multiply", [{'type': 'address', 'name': 'to'}, {'type': 'uint256', 'name': 'deposit'}])
    args_signature = func.abi_args_signature(('d3cda913deb6f67967b99d67acdfa1712c293601', 12345))
    assert args_signature == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0009'


def test_abi_args_signature_with_0x_prefixed_address():
    func = Function("multiply", [{'type': 'address', 'name': 'to'}, {'type': 'uint256', 'name': 'deposit'}])
    args_signature = func.abi_args_signature(('0xd3cda913deb6f67967b99d67acdfa1712c293601', 12345))
    assert args_signature == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0009'


def test_contract_return13_function_signature():
    return13 = Function("return13", inputs=[], outputs=[{'type': 'int256', 'name': 'result'}])
    assert return13.abi_signature == 371289913
    assert return13.encoded_abi_signature == '\x16!o9'
    assert return13.get_call_data([]) == '16216f39'


def test_contract_add_function_signature():
    add = Function(
        "add",
        inputs=[{'type': 'int256', 'name': 'a'}, {'type': 'int256', 'name': 'b'}],
        outputs=[{'type': 'int256', 'name': 'result'}],
    )
    assert add.abi_signature == 2784215611
    assert add.encoded_abi_signature == '\xa5\xf3\xc2;'
    assert add.get_call_data((3, 4)) == 'a5f3c23b00000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004'


def test_contract_multiply7_function_signature():
    multiply7 = Function(
        'multiply7',
        inputs=[{'type': 'int256', 'name': 'a'}],
        outputs=[{'type': 'int256', 'name': 'result'}],
    )
    assert multiply7.abi_signature == 3707058097
    assert multiply7.encoded_abi_signature == '\xdc\xf57\xb1'
    assert multiply7.get_call_data((3,)) == 'dcf537b10000000000000000000000000000000000000000000000000000000000000003'
