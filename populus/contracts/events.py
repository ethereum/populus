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
