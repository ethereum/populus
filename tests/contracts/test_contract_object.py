import pytest

from populus.client import Client
from populus.contracts import Contract


contract = {
    'info': {
        'language': 'Solidity',
        'languageVersion': '0',
        'abiDefinition': [
            {
                'inputs': [],
                'constant': False,
                'type': 'function',
                'name': 'return13',
                'outputs': [
                    {'type': 'int256', 'name': 'result'}
                ],
            },
            {
                'inputs': [
                    {'type': 'int256', 'name': 'a'},
                    {'type': 'int256', 'name': 'b'},
                ],
                'constant': False,
                'type': 'function',
                'name': 'add',
                'outputs': [
                    {'type': 'int256', 'name': 'result'}
                ],
            },
            {
                'inputs': [
                    {'type': 'int256', 'name': 'a'},
                ],
                'constant': False,
                'type': 'function',
                'name': 'multiply7',
                'outputs': [
                    {'type': 'int256', 'name': 'result'},
                ],
            },
        ],
        'source': (
            'contract Math {\n        function add(int a, int b) public returns (int result){\n            result = a + b;\n            return result;\n        }\n\n        function multiply7(int a) public returns (int result){\n            result = a * 7;\n            return result;\n        }\n\n        function return13() public returns (int result) {\n            result = 13;\n            return result;\n        }\n}\n'
        ),
        'compilerVersion': '0.9.73',
        'developerDoc': None,
        'userDoc': None,
    },
    'code': (
        '0x606060405260f8806100126000396000f30060606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f3914604b578063a5f3c23b14606a578063dcf537b1146095576049565b005b605460045060e6565b6040518082815260200191505060405180910390f35b607f60048035906020018035906020015060ba565b6040518082815260200191505060405180910390f35b60a460048035906020015060d0565b6040518082815260200191505060405180910390f35b60008183019050805080905060ca565b92915050565b6000600782029050805080905060e1565b919050565b6000600d9050805080905060f5565b9056'
    ),
}


def test_contract_deploy(rpc_server, eth_tester):
    client = Client('127.0.0.1', '8545')

    from_addr = eth_tester.encode_hex(eth_tester.accounts[0])

    Math = Contract(client, 'Math', contract)
    deploy_txn_hash = Math.deploy(client, _from=from_addr)
    receipt = client.get_transaction_receipt(deploy_txn_hash)
    assert receipt
    assert receipt['contractAddress']


@pytest.fixture
def math(rpc_server, eth_tester):
    client = Client('127.0.0.1', '8545')

    from_addr = eth_tester.encode_hex(eth_tester.accounts[0])

    Math = Contract(client, 'Math', contract)

    txn_hash = Math.deploy(client, _from=from_addr)
    receipt = client.get_transaction_receipt(txn_hash)

    math = Math(receipt['contractAddress'])
    return math


def test_contract_function_call_return13(math, eth_tester):
    from_addr = eth_tester.encode_hex(eth_tester.accounts[0])
    ret = math.return13.call(_from=from_addr)
    import ipdb; ipdb.set_trace()
    x = 3
