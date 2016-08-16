import re


from web3.utils.types import (
    is_string,
    is_integer,
    is_boolean,
)
from web3.utils.string import (
    force_text,
)


def is_primitive_type(value):
    return any((
        value is None,
        is_boolean(value),
        is_string(value),
        is_integer(value),
        isinstance(value, float),
    ))


def is_hex_address(value):
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{40}$', force_text(value))


def is_hex_transaction_hash(value):
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{64}$', force_text(value))
