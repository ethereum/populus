from eth_utils import (
    force_bytes,
    force_text,
    is_bytes,
)


def is_prefixed(value, prefix):
    return value.startswith(
        force_bytes(prefix) if is_bytes(value) else force_text(prefix)
    )


def is_dunderscore_prefixed(value):
    return is_prefixed(value, '__')


def remove_dunderscore_prefix(value):
    if is_dunderscore_prefixed(value):
        return value[2:]
    return value
