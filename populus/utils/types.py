import re


from web3.utils.string import (
    is_string,
    force_text,
)


def is_hex_address(value):
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{40}$', force_text(value))


def is_hex_transaction_hash(value):
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{64}$', force_text(value))
