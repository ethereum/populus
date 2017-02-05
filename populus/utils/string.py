import sys

from web3.utils.string import (  # noqa: F401
    force_bytes,
    force_text,
    coerce_args_to_text,
)


def normalize_class_name(value):
    """
    For `type()` calls:
    * Python 2 wants `str`
    * Python 3.4 wants `str`
    * Python 3.5 doesn't care.
    """
    if sys.version_info.major == 2:
        return force_bytes(value)
    else:
        return force_text(value)
