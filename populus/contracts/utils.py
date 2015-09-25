from ethereum import utils as ethereum_utils
from ethereum import abi
import binascii


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
    res = abi.decode_abi(
        types,
        binascii.a2b_hex(strip_0x_prefix(outputs)),
    )
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


def get_max_gas(rpc_client, scale=0.95):
    latest_block = rpc_client.get_block_by_number('latest')
    max_gas_hex = latest_block['gasLimit']
    max_gas = int(max_gas_hex, 16)
    return int(max_gas * scale)


def deploy_contract(rpc_client, contract_class, constructor_args=None, **kwargs):
    if 'data' in kwargs:
        raise ValueError("Cannot supply `data` for contract deployment")

    if constructor_args is None:
        constructor_args = []

    kwargs['data'] = contract_class.get_deploy_data(*constructor_args)
    txn_hash = rpc_client.send_transaction(**kwargs)
    return txn_hash
