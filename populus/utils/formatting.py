from web3.utils.formatting import (  # noqa: F401
    remove_0x_prefix,
    add_0x_prefix,
    is_prefixed,
)


def is_dunderscore_prefixed(value):
    return is_prefixed(value, '__')


def remove_dunderscore_prefix(value):
    if is_dunderscore_prefixed(value):
        return value[2:]
    return value
