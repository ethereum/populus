from ethereum import utils as ethereum_utils
from ethereum import abi

from populus.contracts.common import ContractBound
from populus.contracts.utils import (
    clean_args,
)

GAS_LIMIT_FRACTION = 0.9


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
        prefix = self.encoded_abi_signature
        suffix = self.abi_args_signature(args)
        data = "{0}{1}".format(prefix, suffix)
        return ethereum_utils.encode_hex(data)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        else:
            return obj._meta.functions[self.name]

    def __call__(self, *args, **kwargs):
        if self.constant:
            return self.call(*args, **kwargs)
        return self.sendTransaction(*args, **kwargs)

    def s(self, *args, **kwargs):
        if self.constant:
            return self(*args, **kwargs)
        max_wait = kwargs.pop('max_wait', 60)
        txn_hash = self(*args, **kwargs)
        txn_receipt = self.contract._meta.blockchain_client.wait_for_transaction(
            txn_hash,
            max_wait=max_wait
        )
        return txn_hash, txn_receipt

    def sendTransaction(self, *args, **kwargs):
        data = self.get_call_data(args)

        if 'gas' not in kwargs:
            # The gasLimit value on the geth chain seems to continuously
            # decline after every block. We use a value of gas
            # slightly less than the get_max_gas value so that when
            # the transaction gets processed, the gas value we send
            # is still less than the gasLimit value when our transaction
            # eventually gets processed.
            kwargs['gas'] = int(
                GAS_LIMIT_FRACTION * self.contract._meta.blockchain_client.get_max_gas()
            )

        return self.contract._meta.blockchain_client.send_transaction(
            to=self.contract._meta.address,
            data=data,
            **kwargs
        )

    def call(self, *args, **kwargs):
        raw = kwargs.pop('raw', False)
        data = self.get_call_data(args)

        output = self.contract._meta.blockchain_client.call(
            to=self.contract._meta.address,
            data=data,
            **kwargs
        )
        if raw:
            return output
        return self.cast_return_data(output)


def validate_argument(_type, value):
    base, sub, arr_list = abi.process_type(_type)

    if arr_list:
        arr_value, remainder = arr_list[-1], arr_list[:-1]
        if arr_value and len(value) != arr_value[0]:
            return False
        subtype = ''.join((base, sub, ''.join((str(v) for v in remainder))))
        return all(validate_argument(subtype, v) for v in value)
    elif base == 'int':
        if not isinstance(value, (int, long)):
            return False
        exp = int(sub)
        lower_bound = -1 * 2 ** exp / 2
        upper_bound = (2 ** exp) / 2 - 1
        return lower_bound <= value <= upper_bound
    elif base == 'uint':
        if not isinstance(value, (int, long)):
            return False
        exp = int(sub)
        lower_bound = 0
        upper_bound = (2 ** exp) - 1
        return lower_bound <= value <= upper_bound
    elif base == 'address':
        if not isinstance(value, basestring):
            return False
        _value = value[2:] if value.startswith('0x') else value
        if set(_value).difference('1234567890abcdef'):
            return False
        return len(_value) == 40
    elif base == 'bytes':
        if not isinstance(value, basestring):
            return False
        try:
            max_length = int(sub)
        except ValueError:
            if sub == '':
                return True
            raise
        return len(value) <= max_length
    elif base == 'string':
        return isinstance(value, basestring)
    else:
        raise ValueError("Unsupported base: '{0}'".format(base))


class FunctionGroup(object):
    def __init__(self, functions):
        self.functions = functions

    def __str__(self):
        return "\n".join((
            "{0}: {1}".format(i, f.signature) for i, f in enumerate(self.functions)
        ))

    @property
    def name(self):
        return self.functions[0].name

    def _bind(self, contract):
        [f._bind(contract) for f in self.functions]

    def __call__(self, *args, **kwargs):
        function = self.get_function_for_call_signature(args)
        return function(*args, **kwargs)

    def sendTransaction(self, *args, **kwargs):
        function = self.get_function_for_call_signature(args)
        return function.sendTransaction(*args, **kwargs)

    def call(self, *args, **kwargs):
        function = self.get_function_for_call_signature(args)
        return function.call(*args, **kwargs)

    def s(self, *args, **kwargs):
        function = self.get_function_for_call_signature(args)
        return function.s(*args, **kwargs)

    def get_function_for_call_signature(self, args):
        candidates = []
        for function in self.functions:
            if len(function.inputs) != len(args):
                continue
            argument_validity = tuple(
                validate_argument(arg_meta['type'], arg)
                for arg_meta, arg
                in zip(function.inputs, args)
            )
            if not all(argument_validity):
                continue
            candidates.append(function)
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) == 0:
            raise TypeError("No functions matched the calling signature")
        else:
            raise TypeError("More than one function matched.")

    def abi_args_signature(self, args):
        function = self.get_function_for_call_signature(args)
        return function.abi_args_signature(args)

    def get_call_data(self, args):
        function = self.get_function_for_call_signature(args)
        return function.get_call_data(args)

    @property
    def input_types(self):
        raise AttributeError("You must access this function on the correct sub-function")

    @property
    def signature(self):
        raise AttributeError("You must access this function on the correct sub-function")

    @property
    def abi_signature(self):
        raise AttributeError("You must access this function on the correct sub-function")

    @property
    def encoded_abi_signature(self):
        raise AttributeError("You must access this function on the correct sub-function")

    @property
    def output_types(self):
        raise AttributeError("You must access this function on the correct sub-function")

    def cast_return_data(self, outputs):
        raise AttributeError("You must access this function on the correct sub-function")
