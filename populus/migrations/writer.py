import os
import functools

from populus.utils.types import (
    is_primitive_type,
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


def writer_fn(fn):
    @functools.wraps(fn)
    def inner(file_obj, value, level=0, prefix='', suffix='', newline=True, *args, **kwargs):
        if prefix is not None:
            file_obj.write(indent(prefix, level))

        fn(file_obj, value=value, level=level, *args, **kwargs)

        if suffix:
            file_obj.write(suffix)

        if newline:
            file_obj.write('\n')
    return inner


@writer_fn
def write_primitive_type(file_obj, value, *args, **kwargs):
    file_obj.write(repr(value))


@writer_fn
def write_list(file_obj, value, level=0, *args, **kwargs):
    if not value:
        file_obj.write('[]')
        return

    file_obj.write('[\n')

    for item in value:
        write_value(file_obj, item, level=level + 1, suffix=",")

    file_obj.write(indent(']', level))


@writer_fn
def write_dict(file_obj, value, level=0, *args, **kwargs):
    if not value:
        file_obj.write('{}')
        return

    file_obj.write('{\n')

    for key, item in value.items():
        write_value(file_obj, key, level=level + 1, newline=False)
        file_obj.write(": ")
        write_value(file_obj, item, level=level + 1, prefix=None, newline=False)
        file_obj.write(",\n")

    file_obj.write(indent('}', level))


@writer_fn
def write_deconstructable(file_obj, value, level=0, *args, **kwargs):
    constructor_import_path, construct_args, construct_kwargs = value.deconstruct()
    # TODO: figure out how to do imports.

    _, _, constructor = constructor_import_path.rpartitian('.')
    file_obj.write(constructor)
    if not construct_args and not construct_kwargs:
        file_obj.write("()")
        return

    file_obj.write("(\n")

    for construct_arg in construct_args:
        write_value(file_obj, construct_arg, level=level + 1, suffix=",")

    for construct_kwarg_name, construct_kwarg_value in construct_kwargs.items():
        write_assignment(
            file_obj,
            construct_kwarg_name,
            construct_kwarg_value,
            level=level + 1,
            suffix=",",
            assignment_operator="=",
        )
    file_obj.write(indent(")", level))


def write_value(file_obj, value, *args, **kwargs):
    if is_primitive_type(value):
        write_primitive_type(file_obj, value, *args, **kwargs)
    elif isinstance(value, list):
        write_list(file_obj, value, *args, **kwargs)
    elif isinstance(value, dict):
        write_dict(file_obj, value, *args, **kwargs)
    elif hasattr(value, 'deconstruct'):
        write_deconstructable(file_obj, value, *args, **kwargs)
    else:
        raise ValueError("Unsupported type: {0!r}".format(type(value)))


def write_assignment(file_obj, name, value, assignment_operator=" = ", *args, **kwargs):
    write_value(
        file_obj,
        value,
        prefix="{0}{1}".format(name, assignment_operator),
        *args,
        **kwargs
    )


def write_empty_migration(file_obj, migration_id, compiled_contracts):
    file_obj.write("# -*- coding: utf-8 -*-\n")
    file_obj.write("from __future__ import unicode_literals\n")
    file_obj.write("\n")
    file_obj.write("from populus import migrations\n")
    file_obj.write("\n")
    file_obj.write("\n")
    file_obj.write("class Migration(migrations.Migration):\n")
    file_obj.write("\n")
    write_assignment(file_obj, 'migration_id', migration_id, level=1)
    write_assignment(file_obj, 'dependencies', [], level=1)
    write_assignment(file_obj, 'operations', [], level=1)
    write_assignment(
        file_obj,
        name='compiled_contracts',
        value=compiled_contracts,
        level=1,
        newline=True,
    )


def write_migration(file_obj, migration_class):
    file_obj.write("# -*- coding: utf-8 -*-\n")
    file_obj.write("from __future__ import unicode_literals\n")
    file_obj.write("\n")
    file_obj.write("from populus import migrations\n")
    file_obj.write("\n")
    file_obj.write("\n")
    file_obj.write("class Migration(migrations.Migration):\n")
    file_obj.write("\n")
    write_assignment(file_obj, 'migration_id', migration_class.migration_id, level=1)
    write_assignment(file_obj, 'dependencies', migration_class.dependencies, level=1)
    write_assignment(file_obj, 'operations', migration_class.operations, level=1)
    write_assignment(
        file_obj,
        name='compiled_contracts',
        value=migration_class.compiled_contracts,
        level=1,
        newline=True,
    )
