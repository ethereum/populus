from collections import Mapping
import itertools

from .functional import (
    cast_return_to_dict,
)


@cast_return_to_dict
def dict_merge(left, right):
    """
    Recursive non-mutating merge of two dictionaries.  Items in `left` take
    precidence.
    """
    for key in itertools.chain(left.keys(), right.keys()):
        if key not in right:
            yield key, left[key]
        elif key not in left:
            yield key, right[key]
        elif isinstance(left[key], Mapping) and isinstance(right[key], Mapping):
            yield key, dict_merge(left[key], right[key])
        else:
            yield key, left[key]
