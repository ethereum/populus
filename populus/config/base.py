import copy
import functools
import warnings

import anyconfig

from eth_utils import (
    to_tuple,
)

from populus.exceptions import (
    ValidationError,
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
from populus.config.helpers import (
    get_empty_config,
    resolve_config,
)

from .validation import (
    validate_config,
)


def deprecated_if_no_refs(message):
    '''
    Decorate a deprecated function, with info about what to use instead, like:

    @deprecated_for("toBytes()")
    def toAscii(arg):
        ...
    '''
    def decorator(to_wrap):
        @functools.wraps(to_wrap)
        def wrapper(self, *args, **kwargs):
            if not self.allow_refs:
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    message,
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter('default', DeprecationWarning)
            return to_wrap(self, *args, **kwargs)
        return wrapper
    return decorator


class Config(object):
    parent = None
    default_config_info = None
    _wrapped = None
    allow_refs = None

    def __init__(self, config=None, parent=None, schema=None, allow_refs=True):
        self.allow_refs = allow_refs

        if config is None:
            config = get_empty_config()
        elif isinstance(config, dict) and hasattr(anyconfig, 'to_container'):
            config = anyconfig.to_container(config)

        self._wrapped = config
        self.parent = parent
        self.schema = schema

        if self.schema is not None:
            self.validate()

        if not self.allow_refs:
            if self.has_references:
                raise ValidationError(
                    "This config object was initialized with allow_refs=False "
                    "but the configuration contains references."
                )
            elif self.parent is not None:
                raise ValidationError(
                    "This config object was configured with a `parent`.  This "
                    "functionality is not compatable with allow_refs=True"
                )

    def validate(self):
        validate_config(self._wrapped)

    #
    # DEPRECATED $ref logic
    #
    @property
    def has_references(self):
        has_refs = any(
            item[0].rpartition(".")[-1] == "$ref"
            for item
            in self.items(flatten=True)
        )
        return has_refs

    @deprecated_if_no_refs(
        "The `$ref` API has been deprecated and is slated for removal"
    )
    def get_master_config(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_master_config()

    @deprecated_if_no_refs(
        "The `$ref` API has been deprecated and is slated for removal"
    )
    def unref(self):
        while self.has_references():
            for key, value in self.items(flatten=True):
                prefix, _, leaf_key = key.rpartition('.')
                if leaf_key == "$ref":
                    self[prefix] = self.get(prefix)

    @deprecated_if_no_refs(
        "The `$ref` API has been deprecated and is slated for removal"
    )
    def resolve(self, value):
        if isinstance(value, dict):
            return resolve_config(value, self.get_master_config())
        else:
            return value

    #
    # Core config API
    #
    def get(self, key, default=None):
        try:
            value = get_nested_key(self._wrapped, key)
        except KeyError:
            return default

        if self.allow_refs:
            return self.resolve(value)
        else:
            return value

    def get_config(self, key, config_class=None):
        if config_class is None:
            config_class = Config
        try:
            value = self.get(key)
            if self.allow_refs:
                return config_class(copy.deepcopy(value), parent=self)
            else:
                return config_class(copy.deepcopy(value))

        except KeyError:
            return config_class(get_empty_config(), parent=self)

    def pop(self, key, default=empty):
        try:
            value = pop_nested_key(self._wrapped, key)
        except KeyError:
            if default is empty:
                raise KeyError(
                    "Key '{0}' not found in {1}".format(key, self._wrapped)
                )
            else:
                value = default

        if self.allow_refs:
            return self.resolve(value)
        else:
            return value

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
            if self.allow_refs:
                return self.resolve(get_nested_key(self._wrapped, key))
            else:
                return get_nested_key(self._wrapped, key)
        except KeyError:
            raise KeyError(
                "Key '{0}' not found in {1}".format(
                    key, self._wrapped
                )
            )

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
