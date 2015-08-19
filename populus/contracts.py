from ethereum import utils as ethereum_utils
from ethereum.abi import encode_abi


class ContractBase(object):
    def __init__(self, address):
        self.address = address

    @classmethod
    def deploy(cls, client, _from=None, gas=None, gas_price=None, value=None):
        return client.send_transaction(
            _from, gas, gas_price, value, data=cls.code,
        )


class BoundFunction(object):
    def __init__(self, function, client, address):
        self.function = function
        self.client = client
        self.address = address

    def __str__(self):
        return str(self.function)

    def __call__(self, *args, **kwargs):
        return self.sendTransaction(*args, **kwargs)

    def sendTransaction(self, *args, **kwargs):
        data = self.function.get_call_data(args)

        return self.client.send_transaction(
            _from=kwargs['from'],
            to=self.address,
            data=data,
        )

    def call(self, *args, **kwargs):
        data = self.function.get_call_data(args)

        return self.client.call(to=self.address, data=data, **kwargs)


class Function(object):
    def __init__(self, name, inputs=None, outputs=None, constant=False):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.constant = constant

    def __str__(self):
        signature = "{func_name}({arg_types})".format(
            func_name=self.name,
            arg_types=', '.join("{0} {1}".format(*i) for i in self.inputs)
        )
        return signature

    @property
    def input_types(self):
        """
        Iterable of the types this function takes.
        """
        if self.inputs:
            return zip(*self.inputs)[0]
        return []

    @property
    def abi_function_signature(self):
        """
        Compute the bytes4 signature for the function.
        """
        signature = "{func_name}({arg_types})".format(
            func_name=self.name,
            arg_types=','.join(self.input_types),
        )
        return ethereum_utils.big_endian_to_int(ethereum_utils.sha3(signature)[:4])

    def abi_args_signature(self, args):
        """
        Given the calling `args` for the function call, abi encode them.
        """
        return encode_abi(self.input_types, args)

    def get_call_data(self, args):
        """
        TODO: this needs tests.
        """
        prefix = ethereum_utils.zpad(ethereum_utils.encode_int(self.abi_function_signature), 4)
        suffix = ethereum_utils.encode_hex(self.abi_args_signature(args))
        return "{0}{1}".format(prefix, suffix)

    def __get__(self, obj, type=None):
        bound_function = BoundFunction(
            function=self,
            client=obj.client,
            address=obj.address,
        )

        return bound_function


class Event(object):
    def __init__(self, name, inputs):
        assert False, "Not implemented"

    def __call__(self, *args):
        assert False, "Not implemented"


def Contract(client, contract_name, contract):
    abi = contract['info']['abiDefinition']
    _dict = {
        'client': client,
        'code': contract['code'],
        'abi': abi,
    }

    functions = []
    events = []

    for signature_item in abi:
        if signature_item['type'] == 'constructor':
            # Constructors don't need to be part of a contract's methods
            continue

        if signature_item['name'] in _dict:
            raise ValueError("About to overwrite a function signature for duplicate function name {0}".format(signature_item['name']))

        if signature_item['type'] == 'function':
            # make sure we're not overwriting a signature

            func = Function(
                name=signature_item['name'],
                inputs=signature_item['inputs'],
                outputs=signature_item['outputs'],
                constant=signature_item['constant'],
            )
            _dict[signature_item['name']] = func
            functions.append(func)
        elif signature_item['type'] == 'event':
            event = Event(**signature_item)
            _dict[signature_item['name']] = event
            events.append(event)
        else:
            raise ValueError("Unknown signature item '{0}'".format(signature_item))

    docstring = """
    contract {contract_name} {{
    // Events
    {events}

    // Functions
    {functions}
    }}
    """.format(
        contract_name=contract_name,
        functions='\n'.join(str(f) for f in functions),
        events='\n'.join(str(e) for e in events),
    )

    _dict['__doc__'] = docstring

    return type(contract_name, (ContractBase,), _dict)
