from __future__ import unicode_literals

import os
import functools
import codecs
from io import StringIO
from collections import OrderedDict

from web3.utils.string import force_text
from web3.utils.types import (
    is_bytes,
    is_text,
)

from populus.utils.types import (
    is_primitive_type,
)
from populus.utils.module_loading import (
    split_at_longest_importable_path,
)
from .loading import (
    find_project_migrations,
)


def get_next_migration_number(project_dir):
    migration_paths = find_project_migrations(project_dir)
    filenames = [
        os.path.basename(migration_file_path)
        for migration_file_path
        in migration_paths
    ]
    migration_numbers = [
        int(filename.partition('_')[0]) for filename in filenames
    ] + [0]
    return max(migration_numbers) + 1


def indent(text, level=0):
    return "    " * level + text


def serializer_fn(fn):
    @functools.wraps(fn)
    def inner(value, level=0, prefix='', suffix='', newline=True, *args, **kwargs):
        imports = set()
        serialized_value = StringIO()

        if prefix is not None:
            serialized_value.write(indent(prefix, level))

        inner_imports, inner_serialized_value = fn(
            value=value,
            level=level,
            *args,
            **kwargs
        )

        imports |= inner_imports
        serialized_value.write(inner_serialized_value)

        if suffix:
            serialized_value.write(suffix)

        if newline:
            serialized_value.write('\n')
        return imports, serialized_value.getvalue()
    return inner


@serializer_fn
def serialize_primitive_type(value, *args, **kwargs):
    if is_bytes(value):
        return set(), "b'{0}'".format(
            force_text(codecs.encode(force_text(value), 'unicode_escape'))
        )
    elif is_text(value):
        return set(), "'{0}'".format(
            force_text(codecs.encode(value, 'unicode_escape'))
        )
    else:
        return set(), force_text(repr(value))


@serializer_fn
def serialize_list(value, level=0, *args, **kwargs):
    if not value:
        return set(), '[]'

    imports = set()
    serialized_value = StringIO()

    serialized_value.write('[\n')

    for item in value:
        item_imports, item_serialized_value = serialize(
            item,
            level=level + 1,
            suffix=",",
            *args,
            **kwargs
        )

        imports |= item_imports
        serialized_value.write(item_serialized_value)

    serialized_value.write(indent(']', level))

    return imports, serialized_value.getvalue()


@serializer_fn
def serialize_dict(value, level=0, *args, **kwargs):
    if not value:
        return set(), '{}'

    ordered_value = OrderedDict(sorted(value.items(), key=lambda kv: kv[0]))

    imports = set()
    serialized_value = StringIO()

    serialized_value.write('{\n')

    for key, item in ordered_value.items():
        inner_kwargs = dict(**kwargs)
        inner_kwargs.pop('newline', None)

        key_imports, key_serialized_value = serialize(
            key,
            level=level + 1,
            newline=False,
            *args,
            **inner_kwargs
        )

        item_imports, item_serialized_value = serialize(
            item,
            level=level + 1,
            prefix=None,
            newline=False,
            *args,
            **inner_kwargs
        )

        imports |= key_imports
        imports |= item_imports

        serialized_value.write(key_serialized_value)
        serialized_value.write(": ")
        serialized_value.write(item_serialized_value)
        serialized_value.write(",\n")

    serialized_value.write(indent('}', level))

    return imports, serialized_value.getvalue()


@serializer_fn
def serialize_deconstructable(value, level=0, *args, **kwargs):
    import_path, construct_args, construct_kwargs = value.deconstruct()

    ordered_construct_kwargs = OrderedDict(
        sorted(construct_kwargs.items(), key=lambda kv: kv[0])
    )

    import_part, constructor_part = split_at_longest_importable_path(import_path)
    # TODO: This *effectively* just re-joins the two parts but that is ok for
    # now.  Ideally later I can figure out how to do imports in the "from a.b.c
    # import d" but this will do for now.
    constructor = '.'.join((import_part, constructor_part))

    imports = {import_part}
    serialized_value = StringIO()

    serialized_value.write(constructor)
    if not construct_args and not construct_kwargs:
        serialized_value.write("()")
        return imports, serialized_value.getvalue()

    serialized_value.write("(\n")

    inner_kwargs = dict(**kwargs)
    inner_kwargs.pop('suffix', None)

    for construct_arg in construct_args:
        arg_imports, arg_serialized_value = serialize(
            construct_arg,
            level=level + 1,
            suffix=",",
            *args,
            **inner_kwargs
        )

        imports |= arg_imports
        serialized_value.write(arg_serialized_value)

    for construct_kwarg_name, construct_kwarg_value in ordered_construct_kwargs.items():
        kwarg_imports, kwarg_serialized_value = serialize_assignment(
            construct_kwarg_name,
            construct_kwarg_value,
            level=level + 1,
            suffix=",",
            assignment_operator="=",
            *args,
            **kwargs
        )

        imports |= kwarg_imports
        serialized_value.write(kwarg_serialized_value)

    serialized_value.write(indent(")", level))
    return imports, serialized_value.getvalue()


def serialize(value, *args, **kwargs):
    if hasattr(value, 'deconstruct') and callable(value.deconstruct):
        return serialize_deconstructable(value, *args, **kwargs)
    elif is_primitive_type(value):
        return serialize_primitive_type(value, *args, **kwargs)
    elif isinstance(value, list):
        return serialize_list(value, *args, **kwargs)
    elif isinstance(value, dict):
        return serialize_dict(value, *args, **kwargs)
    else:
        raise ValueError("Unsupported type: {0!r}".format(type(value)))


def serialize_assignment(name, value, assignment_operator=" = ", *args, **kwargs):
    return serialize(
        value,
        prefix="{0}{1}".format(name, assignment_operator),
        *args,
        **kwargs
    )


MIGRATION_PROPS = (
    'migration_id',
    'dependencies',
    'operations',
    'compiled_contracts',
)


def write_migration(file_obj, migration_class):
    header = StringIO()
    body = StringIO()

    imports = set()

    body.write("class Migration(migrations.Migration):\n\n")

    for prop_name in MIGRATION_PROPS:
        prop_imports, prop_serialized_value = serialize_assignment(
            prop_name,
            getattr(migration_class, prop_name),
            level=1,
        )

        imports |= prop_imports
        body.write(prop_serialized_value)

    header.write("# -*- coding: utf-8 -*-\n")
    header.write("from __future__ import unicode_literals\n")
    header.write("\n")
    header.write("from populus import migrations\n")
    header.write("\n")

    header.writelines([
        "import {import_path}\n".format(import_path=import_path)
        for import_path in sorted(imports)
    ])

    file_obj.write(header.getvalue())
    file_obj.write("\n")
    file_obj.write(body.getvalue())
