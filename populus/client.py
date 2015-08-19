import json
import requests


def get_transaction_params(_from=None, to=None, gas=None, gas_price=None,
                           value=0, data=None):
    params = {}

    if _from is None:
        raise ValueError("No default from address specified")

    params['from'] = _from

    if to is None and data is None:
        raise ValueError("A `to` address is only optional for contract creation")
    elif to is not None:
        params['to'] = to

    if gas is not None:
        params['gas'] = hex(gas)

    if gas_price is not None:
        params['gasPrice'] = hex(gas_price)

    if value is not None:
        params['value'] = hex(value)

    if data is not None:
        params['data'] = data

    return params


class Client(object):
    _nonce = 0

    def __init__(self, host, port, defaults=None):
        self.host = host
        self.port = port
        self.defaults = defaults or {}
        self.session = requests.session()

    def get_nonce(self):
        self._nonce += 1
        return self._nonce

    def make_rpc_request(self, method, params):
        response = self.session.post(
            "http://{host}:{port}/".format(host=self.host, port=self.port),
            data=json.dumps({
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": self.get_nonce(),
            })
        )
        data = response.json()
        if data and 'error' in data:
            raise ValueError(data)
        return data

    def get_coinbase(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_coinbase
        """
        response = self.make_rpc_request("eth_coinbase", [])
        return response['result']

    def get_gas_price(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gasprice
        """
        response = self.make_rpc_request("eth_gasPrice", [])
        return int(response['result'], 16)

    def get_balance(self, address, block="latest"):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getbalance
        """
        response = self.make_rpc_request("eth_getBalance", [address, block])
        return int(response['result'], 16)

    def get_code(self, address, block="latest"):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcode
        """
        response = self.make_rpc_request("eth_getCode", [address, block])
        return response['result']

    def call(self, _from=None, to=None, gas=None, gas_price=None, value=0,
             data=None, block="latest"):
        params = [
            get_transaction_params(_from, to, gas, gas_price, value, data),
            block,
        ]
        response = self.make_rpc_request("eth_call", params)
        return response['result']

    def send_transaction(self, _from=None, to=None, gas=None, gas_price=None,
                         value=0, data=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction
        """
        if _from is None:
            _from = self.defaults.get('from')

        params = get_transaction_params(_from, to, gas, gas_price, value, data)

        response = self.make_rpc_request("eth_sendTransaction", [params])
        return response['result']

    def get_transaction_receipt(self, txn_hash):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt
        """
        response = self.make_rpc_request("eth_getTransactionReceipt", [txn_hash])
        return response['result']
