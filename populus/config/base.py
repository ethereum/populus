import copy

import anyconfig

from populus.utils.functional import (
    cast_return_to_tuple,
)
from populus.utils.empty import (
    empty,
)
from populus.utils.config import (
    has_nested_key,
    get_nested_key,
    set_nested_key,
    pop_nested_key,
    get_empty_config,
    flatten_config_items,
    resolve_config,
)

from .defaults import (
    apply_default_configs,
)


class Config(object):
    parent = None
    default_config_info = None
    config_for_read = None
    config_for_write = None

    def __init__(self, config=None, default_config_info=None, parent=None):
        if config is None:
            config = get_empty_config()
        elif isinstance(config, dict):
            config = anyconfig.to_container(config)

        if default_config_info is None:
            default_config_info = tuple()
        self.default_config_info = default_config_info
        self.config_for_write = config
        self.config_for_read = apply_default_configs(
            self.config_for_write,
            self.default_config_info,
        )
        self.parent = parent

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
            value = get_nested_key(self.config_for_read, key)
        except KeyError:
            return default
        return self.resolve(value)

    def get_config(self, key, defaults=None):
        try:
            return type(self)(self.resolve(self[key]), defaults, parent=self)
        except KeyError:
            return type(self)(get_empty_config(), defaults, parent=self)

    def pop(self, key, default=empty):
        try:
            value = pop_nested_key(self.config_for_read, key)
        except KeyError:
            if default is empty:
                raise
            else:
                value = default

        try:
            pop_nested_key(self.config_for_write, key)
        except KeyError:
            pass

        return self.resolve(value)

    def setdefault(self, key, value):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    @cast_return_to_tuple
    def keys(self, flatten=False):
        for key, _ in self.items(flatten=flatten):
            yield key

    @cast_return_to_tuple
    def items(self, flatten=False):
        if flatten:
            _items = flatten_config_items(self.config_for_read)
        else:
            _items = self.config_for_read.items()
        for key, value in _items:
            yield key, value

    def update(self, other, **kwargs):
        if isinstance(other, type(self)):
            self.config_for_read.update(copy.deepcopy(other.config_for_read), **kwargs)
            self.config_for_write.update(copy.deepcopy(other.config_for_write), **kwargs)
        else:
            self.config_for_read.update(copy.deepcopy(other), **kwargs)
            self.config_for_write.update(copy.deepcopy(other), **kwargs)

    def __str__(self):
        return str(self.config_for_read)

    def __repr__(self):
        return repr(self.config_for_read)

    def __eq__(self, other):
        return self.config_for_read == other

    def __bool__(self):
        if self.config_for_write:
            return True
        elif not self.default_config_info:
            return False
        else:
            return any(tuple(zip(*self.default_config_info)[1]))

    def __nonzero__(self):
        return self.__bool__()

    def __len__(self):
        return len(self.config_for_read)

    def __getitem__(self, key):
        return self.resolve(get_nested_key(self.config_for_read, key))

    def __setitem__(self, key, value):
        if isinstance(value, type(self)):
            set_nested_key(self.config_for_read, key, value.config_for_read)
            return set_nested_key(self.config_for_write, key, value.config_for_write)
        else:
            set_nested_key(self.config_for_read, key, value)
            return set_nested_key(self.config_for_write, key, value)

    def __contains__(self, key):
        return has_nested_key(self.config_for_read, key)

    def __iter__(self):
        return iter(self.keys())

    def __copy__(self):
        return type(self)(
            copy.copy(self.config_for_write),
            copy.copy(self.default_config_info),
        )

    def __deepcopy__(self, memo):
        return type(self)(
            copy.deepcopy(self.config_for_write, memo),
            copy.deepcopy(self.default_config_info, memo),
        )
