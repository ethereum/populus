import pytest


@pytest.fixture(scope="session")
def math_contract_meta():
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
    return contract


@pytest.fixture(scope="session")
def Math(math_contract_meta):
    from populus.contracts import Contract
    Math = Contract(math_contract_meta, 'Math')
    return Math


@pytest.fixture(scope="session")
def named_contract_meta():
    contract = {
        "code": "0x606060405260405160208060948339016040526060805190602001505b806000600050819055505b50605f8060356000396000f30060606040526000357c01000000000000000000000000000000000000000000000000000000009004806306fdde03146037576035565b005b60406004506056565b6040518082815260200191505060405180910390f35b6000600050548156",
        "info": {
            "abiDefinition": [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "name",
                    "outputs": [
                        {
                            "name": "",
                            "type": "bytes32"
                        }
                    ],
                    "type": "function"
                },
                {
                    "inputs": [
                        {
                            "name": "_name",
                            "type": "bytes32"
                        }
                    ],
                    "type": "constructor"
                }
            ],
            "compilerVersion": "0.9.74",
            "developerDoc": {
                "methods": {}
            },
            "language": "Solidity",
            "languageVersion": "0",
            "source": "contract Named {\n        bytes32 public name;\n\n        function Named(bytes32 _name) {\n                name = _name;\n        }\n}\n",
            "userDoc": {
                "methods": {}
            }
        }
    }
    return contract


@pytest.fixture(scope="session")
def Named(named_contract_meta):
    from populus.contracts import Contract
    Named = Contract(named_contract_meta, 'Named')
    return Named
