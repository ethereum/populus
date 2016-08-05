import re
import sys


if sys.version_info.major == 2:
    integer_types = (int, long)  # NOQA
    bytes_types = (bytes, bytearray)
    text_types = (unicode,)  # NOQA
    string_types = (basestring, bytearray)  # NOQA
else:
    integer_types = (int,)
    bytes_types = (bytes, bytearray)
    text_types = (str,)
    string_types = (bytes, str, bytearray)


def is_integer(value):
    return isinstance(value, integer_types) and not isinstance(value, bool)


def is_bytes(value):
    return isinstance(value, bytes_types)


def is_text(value):
    return isinstance(value, text_types)


def is_string(value):
    return isinstance(value, string_types)


def is_boolean(value):
    return isinstance(value, bool)


def is_object(obj):
    return isinstance(obj, dict)


def is_array(obj):
    return isinstance(obj, list)


def is_hex_address(value):
    from .string import force_text
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{40}$', force_text(value))


def is_hex_transaction_hash(value):
    from .string import force_text
    return is_string(value) and re.match(r'^(0x)?[a-fA-F0-9]{64}$', force_text(value))
