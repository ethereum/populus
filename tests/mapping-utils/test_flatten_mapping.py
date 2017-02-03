import pytest

import collections

from populus.utils.mappings import (
    flatten_mapping,
)


EMPTY_CONFIG = {}
SIMPLE_FLAT_CONFIG = collections.OrderedDict((('a', 1), ('b', 2)))
NESTED_ONE_LEVEL = collections.OrderedDict((
    ('a', collections.OrderedDict((('aa', 11), ('ab', 22)))),
    ('b', 2),
    ('c', collections.OrderedDict((('ca', 11), ('cb', 22)))),
))
NESTED_TWO_LEVELS = collections.OrderedDict((
    ('a', collections.OrderedDict((('aa', 11), ('ab', 22)))),
    ('b', 2),
    ('c', collections.OrderedDict((('ca', 11), ('cb', 22)))),
    (
        'd',
        collections.OrderedDict((
            ('da', 11),
            ('db', collections.OrderedDict((('dba', 111), ('dbb', 222)))),
            ('dc', 33),
        ))
    ),
))


@pytest.mark.parametrize(
    'config,expected',
    (
        (EMPTY_CONFIG, tuple()),
        (SIMPLE_FLAT_CONFIG, (('a', 1), ('b', 2))),
        (NESTED_ONE_LEVEL, (
            ('a.aa', 11),
            ('a.ab', 22),
            ('b', 2),
            ('c.ca', 11),
            ('c.cb', 22),
        )),
        (NESTED_TWO_LEVELS, (
            ('a.aa', 11),
            ('a.ab', 22),
            ('b', 2),
            ('c.ca', 11),
            ('c.cb', 22),
            ('d.da', 11),
            ('d.db.dba', 111),
            ('d.db.dbb', 222),
            ('d.dc', 33),
        )),
    )
)
def test_flattening_config_items(config, expected):
    actual = flatten_mapping(config)
    assert actual == expected
