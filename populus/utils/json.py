import collections

from .types import (
    is_primitive_type,
)


def normalize_object_for_json(obj):
    if is_primitive_type(obj):
        return obj
    elif isinstance(obj, (collections.Sequence, collections.Set)):
        return [
            normalize_object_for_json(value)
            for value
            in obj
        ]
    elif isinstance(obj, collections.Mapping):
        return {
            normalize_object_for_json(key): normalize_object_for_json(value)
            for key, value
            in obj.items()
        }
    else:
        raise TypeError("Unable to normalize object of type: {0}".format(type(obj)))
