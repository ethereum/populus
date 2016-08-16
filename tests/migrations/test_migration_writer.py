from __future__ import unicode_literals

import pytest
from io import StringIO

import textwrap
from collections import OrderedDict

from populus.migrations import (
    Migration,
)
from populus.migrations.operations import (
    Operation,
)
from populus.migrations.writer import (
    serialize_primitive_type,
    serialize_list,
    serialize_dict,
    serialize_assignment,
    serialize_deconstructable,
    write_migration,
)

@pytest.mark.parametrize(
    'value,fn_kwargs,expected_imports,expected_value',
    (
        ("1234", {}, set(), "'1234'\n"),
        (b"1234", {}, set(), "b'1234'\n"),
        (1234, {}, set(), "1234\n"),
        (1234.5678, {}, set(), "1234.5678\n"),
        ("1234", {'level': 1}, set(), "    '1234'\n"),
        (b"1234", {'level': 1}, set(), "    b'1234'\n"),
        (1234, {'level': 1}, set(), "    1234\n"),
        (1234.5678, {'level': 1}, set(), "    1234.5678\n"),
    )
)
def test_serialize_primitive_type(value,
                                  fn_kwargs,
                                  expected_imports,
                                  expected_value):
    actual_imports, actual_value = serialize_primitive_type(value, **fn_kwargs)

    assert actual_imports == expected_imports
    assert actual_value == expected_value


@pytest.mark.parametrize(
    'value,fn_kwargs,expected_imports,expected_value',
    (
        ([], {}, set(), "[]\n"),
        ([1, 2], {}, set(), """[
    1,
    2,
]\n"""),
        ([1, 2], {'level': 1}, set(), """    [
        1,
        2,
    ]\n"""),
        (['a', 'b', b'c'], {}, set(), """[
    'a',
    'b',
    b'c',
]\n"""),
        ([[1, 2], ['a', 'b']], {}, set(), """[
    [
        1,
        2,
    ],
    [
        'a',
        'b',
    ],
]\n"""),
    ),
)
def test_serialize_list_type(value,
                             fn_kwargs,
                             expected_imports,
                             expected_value):
    actual_imports, actual_value = serialize_list(value, **fn_kwargs)

    assert actual_imports == expected_imports
    assert actual_value == expected_value


@pytest.mark.parametrize(
    'value,fn_kwargs,expected_imports,expected_value',
    (
        ({}, {}, set(), "{}\n"),
        (OrderedDict((('a', 1), ('b', 2))), {}, set(), """{
    'a': 1,
    'b': 2,
}\n"""),
        (OrderedDict((('a', 1), ('b', 2))), {'level': 1}, set(), """    {
        'a': 1,
        'b': 2,
    }\n"""),
        (OrderedDict((('z', 1), ('a', 2))), {}, set(), """{
    'a': 2,
    'z': 1,
}\n"""),
    ),
)
def test_serialize_dict_type(value,
                             fn_kwargs,
                             expected_imports,
                             expected_value):
    actual_imports, actual_value = serialize_dict(value, **fn_kwargs)

    assert actual_imports == expected_imports
    assert actual_value == expected_value


@pytest.mark.parametrize(
    'name,value,fn_kwargs,expected_imports,expected_value',
    (
        ('x', 3, {}, set(), "x = 3\n"),
        ('x', [], {}, set(), "x = []\n"),
        ('arst', 'arst', {}, set(), "arst = 'arst'\n"),
        ('arst', 'arst', {'level': 2}, set(), "        arst = 'arst'\n"),
        ('tsra', [1, 2], {}, set(), """tsra = [
    1,
    2,
]\n"""),
        ('tsra', [1, 2], {'level': 1}, set(), """    tsra = [
        1,
        2,
    ]\n"""),
    ),
)
def test_serialize_assignment(name,
                              value,
                              fn_kwargs,
                              expected_imports,
                              expected_value):
    actual_imports, actual_value = serialize_assignment(name, value, **fn_kwargs)

    assert actual_imports == expected_imports
    assert actual_value == expected_value


class Foo(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def deconstruct(self):
        return (
            '.'.join((self.__class__.__module__, self.__class__.__name__)),
            (self.a, self.b),
            {},
        )


@pytest.mark.parametrize(
    'value,fn_kwargs,expected_imports,expected_value',
    (
        (Foo(1, 2), {}, {__name__}, """{__name__}.Foo(
    1,
    2,
)\n""".format(__name__=__name__)),
    ),
)
def test_serialize_deconstructable(value,
                                   fn_kwargs,
                                   expected_imports,
                                   expected_value):
    actual_imports, actual_value = serialize_deconstructable(value, **fn_kwargs)

    assert actual_imports == expected_imports
    assert actual_value == expected_value


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
            'abi': [],
            'code': '0x1234',
            'code_runtime': '0x1234',
        },
        'ContractB': {
            'abi': [],
            'code': '0x5678',
            'code_runtime': '0x5678',
        },
    }
""").strip() + "\n")


def test_serialize_empty_migration():
    class TestMigration(Migration):

        migration_id = '0001_initial'
        dependencies = []
        operations = []
        compiled_contracts = {
            'ContractA': {
                'abi': [],
                'code': '0x1234',
                'code_runtime': '0x1234',
            },
            'ContractB': {
                'abi': [],
                'code': '0x5678',
                'code_runtime': '0x5678',
            },
        }

    f = StringIO()
    write_migration(f, TestMigration)
    assert f.getvalue() == EXPECTED_EMPTY_MIGRATION_CONTENT
