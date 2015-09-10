import binascii
import copy
import hashlib
import itertools

from ethereum import utils as ethereum_utils
from ethereum import abi

from populus.utils import wait_for_transaction


def decode_single(typ, data):
    base, sub, _ = abi.process_type(typ)

    if base == 'address':
        return '0x' + data[-40:]
    elif base == 'string' or base == 'bytes' or base == 'hash':
        if sub:
            bytes = ethereum_utils.int_to_32bytearray(int(data, 16))
            while bytes and bytes[-1] == 0:
                bytes.pop()
            if bytes:
                return ''.join(chr(b) for b in bytes)
        else:
            num_bytes = int(data[64 + 2:128 + 2], 16)
            bytes_as_hex = data[2 + 128:2 + 128 + (2 * num_bytes)]
            return ethereum_utils.decode_hex(bytes_as_hex)
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


class ContractBound(object):
    _contract = None

    def _bind(self, contract):
        self._contract = contract

    @property
    def contract(self):
        if self._contract is None:
            raise AttributeError("Function not bound to a contract")
        return self._contract


class Function(ContractBound):
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

    def __copy__(self):
        return self.__class__(self.name, self.inputs, self.outputs, self.constant)

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
        else:
            return obj._meta.functions[self.name]

    def __call__(self, *args, **kwargs):
        if self.constant:
            return self.call(*args, **kwargs)
        return self.sendTransaction(*args, **kwargs)

    def sendTransaction(self, *args, **kwargs):
        data = self.get_call_data(args)

        if 'gas' not in kwargs:
            kwargs['gas'] = get_max_gas(self.contract._meta.rpc_client)

        return self.contract._meta.rpc_client.send_transaction(
            to=self.contract._meta.address,
            data=data,
            **kwargs
        )

    def call(self, *args, **kwargs):
        raw = kwargs.pop('raw', False)
        data = self.get_call_data(args)

        output = self.contract._meta.rpc_client.call(
            to=self.contract._meta.address,
            data=data,
            **kwargs
        )
        if raw:
            return output
        return self.cast_return_data(output)


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


class ContractBase(object):
    def __init__(self, address, rpc_client):
        functions = {fn.name: fn for fn in (copy.copy(f) for f in self._config._functions)}
        events = {ev.name: ev for ev in (copy.copy(e) for e in self._config._events)}
        for obj in itertools.chain(functions.values(), events.values()):
            obj._bind(self)
        self._meta = ContractMeta(address, rpc_client, functions, events)

    def __str__(self):
        return "{name}({address})".format(name=self.__class__.__name__, address=self.address)

    @classmethod
    def get_deploy_data(cls, *args):
        data = cls._config.code
        if args:
            if cls._config.constructor is None:
                raise ValueError("This contract does not appear to have a constructor")
            data += ethereum_utils.encode_hex(cls._config.constructor.abi_args_signature(args))

        return data

    #
    #  Instance Methods
    #
    def get_balance(self, block="latest"):
        return self._meta.rpc_client.get_balance(self._meta.address, block=block)


class ContractMeta(object):
    """
    Instance level contract data.
    """
    def __init__(self, address, rpc_client, functions, events):
        self.address = address
        self.rpc_client = rpc_client
        self.functions = functions
        self.events = events


class Config(object):
    """
    Contract (class) level contract data.
    """
    def __init__(self, code, source, abi, functions, events, constructor):
        self.code = code
        self.source = source
        self.abi = abi
        self._functions = functions
        self._events = events
        self.constructor = constructor


def Contract(contract_meta, contract_name=None):
    _abi = contract_meta['info']['abiDefinition']
    code = contract_meta['code']
    source = contract_meta['info']['source']

    if contract_name is None:
        contract_name = "Unknown-{0}".format(hashlib.md5(code).hexdigest())

    functions = []
    events = []
    constructor = None

    _dict = {}

    for signature_item in _abi:
        if signature_item['type'] == 'constructor':
            # Constructors don't need to be part of a contract's methods
            if signature_item.get('inputs'):
                constructor = Function(
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
            event = Event(
                name=signature_item['name'],
                inputs=signature_item['inputs'],
                anonymous=signature_item['anonymous'],
            )
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
    _dict['_config'] = Config(code, source, _abi, functions, events, constructor)

    return type(str(contract_name), (ContractBase,), _dict)


def deploy_contract(rpc_client, contract_class, constructor_args=None, **kwargs):
    if 'data' in kwargs:
        raise ValueError("Cannot supply `data` for contract deployment")

    if constructor_args is None:
        constructor_args = []

    kwargs['data'] = contract_class.get_deploy_data(*constructor_args)
    txn_hash = rpc_client.send_transaction(**kwargs)
    return txn_hash


def get_contract_address_from_txn(rpc_client, txn_hash, max_wait=0):
    txn_receipt = wait_for_transaction(rpc_client, txn_hash, max_wait)

    return txn_receipt['contractAddress']


def get_max_gas(rpc_client, scale=0.95):
    latest_block = rpc_client.get_block_by_number('latest')
    max_gas_hex = latest_block['gasLimit']
    max_gas = int(max_gas_hex, 16)
    return int(max_gas * scale)
