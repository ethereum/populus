from io import StringIO
import textwrap
import collections

from populus.migrations.writer import (
    write_primitive_type,
    write_list,
    write_dict,
    write_assignment,
    write_empty_migration,
)


EXPECTED_PRIMITIVE_TYPE_TEXT = textwrap.dedent(("""
'1234'
b'1234'
1234
1234.5678
    '1234'
    b'1234'
    1234
    1234.5678
""").strip() + "\n")

def test_write_primitive_type():
    f = StringIO()
    write_primitive_type(f, "1234")
    write_primitive_type(f, b"1234")
    write_primitive_type(f, 1234)
    write_primitive_type(f, 1234.5678)

    write_primitive_type(f, "1234", level=1)
    write_primitive_type(f, b"1234", level=1)
    write_primitive_type(f, 1234, level=1)
    write_primitive_type(f, 1234.5678, level=1)

    assert f.getvalue() == EXPECTED_PRIMITIVE_TYPE_TEXT


EXPECTED_ARRAY_TEXT = textwrap.dedent(("""
[]
[
    '1234',
    b'1234',
    1234,
    1234.5678,
]
    [
        '1234',
        b'1234',
        1234,
        1234.5678,
    ]
[
    [
        1,
        2,
        3,
    ],
    [
        4,
        5,
        6,
    ],
]
""").strip() + "\n")

def test_write_list_type():
    f = StringIO()
    value = [
        "1234",
        b"1234",
        1234,
        1234.5678,
    ]

    write_list(f, [])
    write_list(f, value)
    write_list(f, value, level=1)
    write_list(f, [[1, 2, 3], [4, 5, 6]])

    assert f.getvalue() == EXPECTED_ARRAY_TEXT


EXPECTED_DICT_TEXT = textwrap.dedent(("""
{}
{
    'a': 1,
    'b': 2,
}
""").strip() + "\n")

def test_write_dict_type():
    f = StringIO()

    write_dict(f, {})
    write_dict(f, collections.OrderedDict((
        ('a', 1),
        ('b', 2),
    )))

    assert f.getvalue() == EXPECTED_DICT_TEXT



EXPECTED_ASSIGNMENT_TEXT = textwrap.dedent(("""
x = 3
x = {
    'a': 3,
}
    x = {
        'a': 3,
    }
""").strip() + "\n")


def test_write_assignment():
    f = StringIO()

    write_assignment(f, 'x', 3)
    write_assignment(f, 'x', {'a': 3})
    write_assignment(f, 'x', {'a': 3}, level=1)

    assert f.getvalue() == EXPECTED_ASSIGNMENT_TEXT


EXPECTED_EMPTY_MIGRATION_CONTENT = textwrap.dedent(("""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from populus import migrations


class Migration(migrations.Migration):

    migration_id = '0001_initial'
    dependencies = []
    operations = []
    compiled_contracts = {
        'ContractA': {
            'code': '0x1234',
            'code_runtime': '0x1234',
            'abi': [],
        },
        'ContractB': {
            'code': '0x5678',
            'code_runtime': '0x5678',
            'abi': [],
        },
    }
""").strip() + "\n")


def test_write_empty_migration():
    f = StringIO()

    compiled_contracts = collections.OrderedDict((
        ('ContractA', collections.OrderedDict((
            ('code', '0x1234'),
            ('code_runtime', '0x1234'),
            ('abi', []),
        ))),
        ('ContractB', collections.OrderedDict((
            ('code', '0x5678'),
            ('code_runtime', '0x5678'),
            ('abi', []),
        ))),
    ))

    write_empty_migration(f, '0001_initial', compiled_contracts)
    assert f.getvalue() == EXPECTED_EMPTY_MIGRATION_CONTENT
