import os
import pprint

from web3.utils.types import (
    is_bytes,
    is_string,
)

from populus.compilation import (
    compile_project_contracts,
)


def indent(text, levels=0):
    return "    " * levels + text


i = indent


def write_primitive_type(file_obj, value, base_indent, newline):
    file_obj.write(
        indent(repr(value), base_indent),
    )

    if newline:
        file_obj.write('\n')


def write_list(file_obj, value, base_indent, newline):
    file_obj.write(indent('[', base_indent))
    for item in value:
        write_value(file_obj, value, base_indent + 1, newline=True):
    file_obj.write(indent(']', base_indent))

    if newline:
        file_obj.write('\n')


def write_value(file_obj, value, *args, **kwargs):
    if isinstance(value, list):
        write_list(file_obj, value, *args, **kwargs)
    elif
    else:
        raise ValueError("Unsupported type")


def write_empty_migration(migration_file_path, migration):
    if os.path.exists(migration_file_path):
        raise ValueError(
            "There is already a migration named {0!r}".format(migration_file_path)
        )
    with open(migration_file_path, 'w') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("from __future__ import unicode_literals\n")
        f.write("\n")
        f.write("from populus import migrations\n")
        f.write("\n")
        f.write("\n")
        f.write("class Migration(migrations.Migration):\n")
        f.write("\n")
        f.write("    migration_id = '{0}'\n".format(migration.migration_id))
        f.write("    dependencies = []\n")
        f.write("    operations = []\n")
        assert False
