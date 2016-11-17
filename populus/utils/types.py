from eth_utils import (
    is_string,
    is_boolean,
    is_number,
)


def is_primitive_type(value):
    return any((
        value is None,
        is_boolean(value),
        is_string(value),
        is_number(value),
    ))
