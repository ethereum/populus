import pytest

from eth_rpc_client import Client

from populus.contracts import Contract

from ethereum import utils as ethereum_utils


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


@pytest.fixture
def Math(rpc_client):
    Math = Contract(rpc_client, 'Math', contract)
    return Math


def test_constructor_with_args(rpc_server, rpc_client, Math, eth_coinbase):
    deploy_txn_hash = Math.deploy(_from=eth_coinbase, args=("John",))
    receipt = rpc_client.get_transaction_receipt(deploy_txn_hash)
    assert receipt
    assert receipt['contractAddress']
    math = Math(receipt['contractAddress'])
    name = math.name.call(_from=eth_coinbase)
    assert name == "John"
