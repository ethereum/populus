import json
import requests


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
        return response.json()

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
        response = self.make_rpc_request("eth_getBalance", [address, block])
        return int(response['result'], 16)

    def send_transaction(self, _from=None, to=None, gas=None, gas_price=None,
                         value=0, data=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction
        """
        params = {}

        if _from is None:
            _from = self.defaults.get('from')
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

        response = self.make_rpc_request("eth_sendTransaction", [params])
        return response['result']

    def get_transaction_receipt(self, txn_hash):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt
        """
        response = self.make_rpc_request("eth_getTransactionReceipt", [txn_hash])
        return response['result']
