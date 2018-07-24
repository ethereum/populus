from eth_utils import (
    to_bytes,
    to_text,
    is_bytes,
)


def is_prefixed(value, prefix):
    return value.startswith(
        to_bytes(prefix) if is_bytes(value) else to_text(prefix)
    )


def is_dunderscore_prefixed(value):
    return is_prefixed(value, '__')


def remove_dunderscore_prefix(value):
    if is_dunderscore_prefixed(value):
        return value[2:]
    return value
