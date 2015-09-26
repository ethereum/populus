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

    @property
    def outputs(self):
        return [input for input in self.inputs if not input['indexed']]

    @property
    def event_topic(self):
        return ethereum_utils.big_endian_to_int(ethereum_utils.sha3(self.signature))

    def get_log_data(self, log_entry):
        return self.cast_return_data(log_entry['data'])
