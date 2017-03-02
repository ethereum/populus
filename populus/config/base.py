import copy

import anyconfig

from eth_utils import (
    to_tuple,
)

from populus.utils.empty import (
    empty,
)
from populus.utils.mappings import (
    has_nested_key,
    get_nested_key,
    set_nested_key,
    pop_nested_key,
    flatten_mapping,
)
from populus.utils.config import (
    get_empty_config,
    resolve_config,
)

from .validation import (
    validate_config,
)


class Config(object):
    parent = None
    default_config_info = None
    _wrapped = None

    def __init__(self, config=None, parent=None, schema=None):
        if config is None:
            config = get_empty_config()
        elif isinstance(config, dict):
            config = anyconfig.to_container(config)

        self._wrapped = config
        self.parent = parent
        self.schema = schema

        if self.schema is not None:
            self.validate()

    def validate(self):
        validate_config(self._wrapped)

    def get_master_config(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_master_config()

    def resolve(self, value):
        if isinstance(value, dict):
            return resolve_config(value, self.get_master_config())
        else:
            return value

    def get(self, key, default=None):
        try:
            value = get_nested_key(self._wrapped, key)
        except KeyError:
            return default
        return self.resolve(value)

    def get_config(self, key, config_class=None):
        if config_class is None:
            config_class = Config
        try:
            return config_class(self.resolve(self[key]), parent=self)
        except KeyError:
            return config_class(get_empty_config(), parent=self)

    def pop(self, key, default=empty):
        try:
            value = pop_nested_key(self._wrapped, key)
        except KeyError:
            if default is empty:
                raise KeyError("Key '{0}' not found in {1}".format(key, self.wrapped))
            else:
                value = default

        return self.resolve(value)

    def setdefault(self, key, value):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    @to_tuple
    def keys(self, flatten=False):
        for key, _ in self.items(flatten=flatten):
            yield key

    @to_tuple
    def items(self, flatten=False):
        if flatten:
            _items = flatten_mapping(self._wrapped)
        else:
            _items = self._wrapped.items()
        for key, value in _items:
            yield key, value

    def update(self, other, **kwargs):
        if isinstance(other, Config):
            self._wrapped.update(copy.deepcopy(other._wrapped), **kwargs)
        else:
            self._wrapped.update(copy.deepcopy(other), **kwargs)

    def __str__(self):
        return str(self._wrapped)

    def __repr__(self):
        return repr(self._wrapped)

    def __eq__(self, other):
        return self._wrapped == other

    def __bool__(self):
        return bool(self._wrapped)

    def __nonzero__(self):
        return self.__bool__()

    def __len__(self):
        return len(self._wrapped)

    def __getitem__(self, key):
        try:
            return self.resolve(get_nested_key(self._wrapped, key))
        except KeyError:
            raise KeyError("Key '{0}' not found in {1}".format(key, self._wrapped))

    def __setitem__(self, key, value):
        if isinstance(value, Config):
            return set_nested_key(self._wrapped, key, value._wrapped)
        else:
            return set_nested_key(self._wrapped, key, value)

    def __delitem__(self, key):
        del self._wrapped[key]

    def __contains__(self, key):
        return has_nested_key(self._wrapped, key)

    def __iter__(self):
        return iter(self.keys())

    def __copy__(self):
        return type(self)(
            copy.copy(self._wrapped),
        )

    def __deepcopy__(self, memo):
        return type(self)(
            copy.deepcopy(self._wrapped, memo),
        )
