import binascii
from ethereum import utils as ethereum_utils
from ethereum import abi


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
            to=self.address,
            data=data,
            **kwargs
        )

    def call(self, *args, **kwargs):
        data = self.function.get_call_data(args)

        output = self.client.call(to=self.address, data=data, **kwargs)
        return self.function.cast_return_data(output)


def decode_single(typ, data):
    base, sub, _ = abi.process_type(typ)

    if base == 'address':
        return '0x' + data[-40:]
    elif base == 'string' or base == 'bytes' or base == 'hash':
        bytes = ethereum_utils.int_to_32bytearray(int(data, 16))
        while bytes and bytes[-1] == 0:
            bytes.pop()
        if bytes:
            return ''.join(chr(b) for b in bytes)
    elif base == 'uint':
        return int(data, 16)
    elif base == 'int':
        o = int(data, 16)
        return (o - 2 ** int(sub)) if o >= 2 ** (int(sub) - 1) else o
    elif base == 'ureal':
        raise NotImplementedError('havent gotten to this')
        high, low = [int(x) for x in sub.split('x')]
        # return big_endian_to_int(data) * 1.0 / 2 ** low
    elif base == 'real':
        raise NotImplementedError('havent gotten to this')
        high, low = [int(x) for x in sub.split('x')]
        # return (big_endian_to_int(data) * 1.0 / 2 ** low) % 2 ** high
    elif base == 'bool':
        return bool(int(data, 16))
    else:
        raise ValueError("Unknown base: `{0}`".format(base))


def decode_multi(types, outputs):
    res = abi.decode_abi(types, binascii.a2b_hex(outputs[2:]))
    return res


def strip_0x_prefix(value):
    if value.startswith('0x'):
        return value[2:]
    return value


def clean_args(*args):
    for _type, arg in args:
        if _type == 'address':
            yield strip_0x_prefix(arg)
        else:
            yield arg


class Function(object):
    def __init__(self, name, inputs=None, outputs=None, constant=False):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.constant = constant

    def __str__(self):
        signature = "{func_name}({arg_types})".format(
            func_name=self.name,
            arg_types=', '.join(
                "{0} {1}".format(i['type'], i['name']) for i in self.inputs
            )
        )
        return signature

    @property
    def input_types(self):
        """
        Iterable of the types this function takes.
        """
        if self.inputs:
            return [i['type'] for i in self.inputs]
        return []

    @property
    def output_types(self):
        """
        Iterable of the types this function takes.
        """
        if self.outputs:
            return [i['type'] for i in self.outputs]
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

    @property
    def encoded_abi_function_signature(self):
        return ethereum_utils.zpad(ethereum_utils.encode_int(self.abi_function_signature), 4)

    def abi_args_signature(self, args):
        """
        Given the calling `args` for the function call, abi encode them.
        """
        if len(self.input_types) != len(args):
            raise ValueError("Expected {0} arguments, only got {1}".format(len(self.input_types), len(args)))  # NOQA
        scrubbed_args = tuple(clean_args(*zip(self.input_types, args)))
        return abi.encode_abi(self.input_types, scrubbed_args)

    def get_call_data(self, args):
        """
        TODO: this needs tests.
        """
        prefix = self.encoded_abi_function_signature
        suffix = self.abi_args_signature(args)
        data = "{0}{1}".format(prefix, suffix)
        return ethereum_utils.encode_hex(data)

    def cast_return_data(self, outputs):
        if len(self.output_types) != 1:
            return decode_multi(self.output_types, outputs)
        output_type = self.output_types[0]

        return decode_single(output_type, outputs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
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


class ContractBase(object):
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return "{name}({address})".format(name=self.__class__.__name__, address=self.address)

    @classmethod
    def deploy(cls, _from=None, gas=None, gas_price=None, value=None, constructor_args=None):
        data = cls.code
        if constructor_args:
            data += ethereum_utils.encode_hex(cls.constructor.abi_args_signature(constructor_args))

        return cls.client.send_transaction(
            _from, gas, gas_price, value, data=data,
        )

    def get_balance(self, block="latest"):
        return self.client.get_balance(self.address, block=block)


def Contract(client, contract_name, contract):
    _abi = contract['info']['abiDefinition']
    _dict = {
        'client': client,
        'code': contract['code'],
        'source': contract['info']['source'],
        'abi': _abi,
    }

    functions = []
    events = []

    for signature_item in _abi:
        if signature_item['type'] == 'constructor':
            # Constructors don't need to be part of a contract's methods
            if signature_item.get('inputs'):
                _dict['constructor'] = Function(
                    name='constructor',
                    inputs=signature_item['inputs'],
                )
            continue

        if signature_item['name'] in _dict:
            # TODO: handle namespace conflicts
            raise ValueError("About to overwrite a function signature for duplicate function name {0}".format(signature_item['name']))  # NOQA

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

    return type(str(contract_name), (ContractBase,), _dict)
