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
    from eth_contract import Contract
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
    from eth_contract import Contract
    Named = Contract(named_contract_meta, 'Named')
    return Named


@pytest.fixture(scope="session")
def logs_events_contract_meta():
    contract = {
        'code': '0x6060604052610116806100126000396000f360606040526000357c0100000000000000000000000000000000000000000000000000000000900480631d3778b41461004457806378549c581461006357610042565b005b6100616004803590602001803590602001803590602001506100d0565b005b610086600480359060200180359060200180359060200180359060200150610088565b005b82847f968e08311bcc13cd5d4feae6a3c87bedb195ab51905c8ec75a10580b5b5854c78484604051808381526020018281526020019250505060405180910390a35b50505050565b827fe5091e521791fb0fb6be999dcb6d5031d9f0a8032185b13790f8d2f95e163b1f8383604051808381526020018281526020019250505060405180910390a25b50505056',
        'info': {
            'abiDefinition': [
                {
                    'constant': False,
                    'inputs': [
                        {'name': 'key', 'type': 'bytes32'},
                        {'name': 'val_a', 'type': 'bytes32'},
                        {'name': 'val_b', 'type': 'uint256'},
                    ],
                    'name': 'logSingleIndex',
                    'outputs': [],
                    'type': 'function'
                },
                {
                    'constant': False,
                    'inputs': [
                        {'name': 'key_a', 'type': 'bytes32'},
                        {'name': 'key_b', 'type': 'bytes32'},
                        {'name': 'val_a', 'type': 'bytes32'},
                        {'name': 'val_b', 'type': 'uint256'},
                    ],
                    'name': 'logDoubleIndex',
                    'outputs': [],
                    'type': 'function'
                },
                {
                    'anonymous': False,
                    'inputs': [
                        {'indexed': True, 'name': 'key', 'type': 'bytes32'},
                        {'indexed': False, 'name': 'val_a', 'type': 'bytes32'},
                        {'indexed': False, 'name': 'val_b', 'type': 'uint256'},
                    ],
                    'name': 'SingleIndex',
                    'type': 'event'
                },
                {
                    'anonymous': False,
                    'inputs': [
                        {'indexed': True, 'name': 'key_a', 'type': 'bytes32'},
                        {'indexed': True, 'name': 'key_b', 'type': 'bytes32'},
                        {'indexed': False, 'name': 'val_a', 'type': 'bytes32'},
                        {'indexed': False, 'name': 'val_b', 'type': 'uint256'},
                    ],
                    'name': 'DoubleIndex',
                    'type': 'event'
                },
            ],
            'compilerVersion': '0.1.3-1736fe80',
            'developerDoc': {
                'methods': {},
            },
            'language': 'Solidity',
            'languageVersion': '0',
            'source': 'contract LogsEvents {\n        event SingleIndex(bytes32 indexed key, bytes32 val_a, uint val_b);\n\n        function logSingleIndex(bytes32 key, bytes32 val_a, uint val_b) public {\n                SingleIndex(key, val_a, val_b);\n        }\n\n        event DoubleIndex(bytes32 indexed key_a, bytes32 indexed key_b, bytes32 val_a, uint val_b);\n\n        function logDoubleIndex(bytes32 key_a, bytes32 key_b, bytes32 val_a, uint val_b) public {\n                DoubleIndex(key_a, key_b, val_a, val_b);\n        }\n}\n',
            'userDoc': {
                'methods': {},
            },
        },
    }
    return contract


@pytest.fixture(scope="session")
def LogsEvents(logs_events_contract_meta):
    from eth_contract import Contract
    LogsEvents = Contract(logs_events_contract_meta, 'LogsEvents')
    return LogsEvents
