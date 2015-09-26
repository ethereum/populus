from ethereum import utils as ethereum_utils

from populus.contracts.utils import (
    decode_multi,
    decode_single,
)


class ContractBound(object):
    _contract = None

    def _bind(self, contract):
        self._contract = contract

    @property
    def contract(self):
        if self._contract is None:
            raise AttributeError("Function not bound to a contract")
        return self._contract

    #
    # ABI Signature
    #
    @property
    def input_types(self):
        """
        Iterable of the types this function takes.
        """
        if self.inputs:
            return [i['type'] for i in self.inputs]
        return []

    @property
    def signature(self):
        signature = "{name}({arg_types})".format(
            name=self.name,
            arg_types=','.join(self.input_types),
        )
        return signature

    @property
    def abi_signature(self):
        """
        Compute the bytes4 signature for the object.
        """
        return ethereum_utils.big_endian_to_int(ethereum_utils.sha3(self.signature)[:4])

    @property
    def encoded_abi_signature(self):
        return ethereum_utils.zpad(ethereum_utils.encode_int(self.abi_signature), 4)

    @property
    def output_types(self):
        """
        Iterable of the types this function takes.
        """
        if self.outputs:
            return [i['type'] for i in self.outputs]
        return []

    def cast_return_data(self, outputs):
        if len(self.output_types) != 1:
            return decode_multi(self.output_types, outputs)
        output_type = self.output_types[0]

        return decode_single(output_type, outputs)
