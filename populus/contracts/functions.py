from ethereum import utils as ethereum_utils
from ethereum import abi

from populus.contracts.common import ContractBound
from populus.contracts.utils import (
    clean_args,
    get_max_gas,
)


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
