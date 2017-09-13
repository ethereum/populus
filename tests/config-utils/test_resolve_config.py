import pytest

from populus.config import (
    Config,
)
from populus.config.helpers import (
    resolve_config,
)


MASTER_CONFIG = Config({
    'a': {
        'a': 'a.a',
    },
    'b': {
        'a': 'b.a',
        'b': 'b.b',
    },
    'c': {
        'a': {
            'a': 'c.a.a',
            'b': 'c.a.b',
        },
        'b': {
            'a': 'c.b.a',
            'b': 'c.b.b',
        },
    },
})


@pytest.mark.parametrize(
    'config,expected',
    (
        ({'b': 'b'}, {'b': 'b'}),
        ({'$ref': 'a'}, {'a': 'a.a'}),
        ({'$ref': 'b'}, {'a': 'b.a', 'b': 'b.b'}),
        ({'$ref': 'c.a'}, {'a': 'c.a.a', 'b': 'c.a.b'}),
        ({'$ref': 'c.b'}, {'a': 'c.b.a', 'b': 'c.b.b'}),
    )
)
def test_resolving_config(config, expected):
    actual = resolve_config(config, MASTER_CONFIG)
    assert actual == expected
