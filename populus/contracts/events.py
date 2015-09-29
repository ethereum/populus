from ethereum import utils as ethereum_utils

from populus.contracts.common import ContractBound


class Event(ContractBound):
    """
    {
        'inputs': [
            {'indexed': False, 'type': 'bytes32', 'name': 'dataHash'},
            {'indexed': False, 'type': 'bytes', 'name': 'data'},
        ],
        'type': 'event',
        'name': 'DataRegistered',
        'anonymous': False,
    }
    """
    def __init__(self, name, inputs, anonymous):
        self.name = name
        self.inputs = inputs
        self.anonymous = anonymous

    def __call__(self, *args):
        pass

    def __copy__(self):
        return self.__class__(self.name, self.inputs, self.anonymous)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        else:
            return obj._meta.events[self.name]

    @property
    def outputs(self):
        return [input for input in self.inputs if not input['indexed']]

    @property
    def event_topic(self):
        return hex(ethereum_utils.big_endian_to_int(
            ethereum_utils.sha3(self.signature)
        )).strip('L')

    def get_transaction_logs(self, txn_hash):
        txn_receipt = self.contract._meta.rpc_client.get_transaction_receipt(txn_hash)
        if txn_receipt is None:
            return None
        return [
            log for log in txn_receipt['logs'] if self.event_topic in log['topics']
        ]

    def get_log_data(self, log_entry):
        values = self.cast_return_data(log_entry['data'])
        return {
            output['name']: value for output, value in zip(self.outputs, values)
        }
