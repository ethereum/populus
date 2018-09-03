from eth_utils import (
    to_text,
)


def normalize_class_name(value):
    """
    For `type()` calls:
    * Python 3.4 wants `str`
    * Python 3.5 doesn't care.
    """
    return to_text(text=value)
