import os
from populus.serpent import (
    get_signature,
    generate_abi,
)


TEST_DIR = os.path.dirname(__file__)

source_file = os.path.join(TEST_DIR, 'projects', 'test-01', 'contracts', 'mul2.se')
source_dir = os.path.dirname(source_file)
source_code = """
def double(x):
    return (x * 2)
"""
named_contract_signature = 'extern mul2.se: [double:[int256]:int256]'
unnamed_contract_signature = 'extern main: [double:[int256]:int256]'


def test_get_signature_from_file(monkeypatch):
    monkeypatch.chdir(source_dir)
    signature = get_signature(input_file=os.path.basename(source_file))
    assert signature == named_contract_signature


def test_get_signature_from_file_strips_path_prefix():
    signature = get_signature(input_file=source_file)
    assert signature == named_contract_signature


def test_get_signature_from_source():
    signature = get_signature(source=source_code)
    assert signature == unnamed_contract_signature

abi_1 = [
    {
        "constant": False,
        "name": "double",
        "inputs": [
            {
                "name": "arg_0",
                "type": "int256",
            },
        ],
        "outputs": [
            {
                "name": "ret_0",
                "type": "int256"
            }
        ],
        "type": "function",
    },
]

def test_abi_generation():
    signature = 'extern main: [double:[int256]:int256]'
    abi = generate_abi(signature)
    assert abi == abi_1
