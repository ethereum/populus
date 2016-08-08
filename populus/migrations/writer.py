import os
import pprint

from web3.utils.types import (
    is_bytes,
    is_string,
)

from populus.compilation import (
    compile_project_contracts,
)


def write_bytes(file_obj, value, base_indent, newline=False):
    if not is_bytes(value):
        raise ValueError("Value must be of type `bytes`")
    file_obj.write(repr(value))

    if newline:
        file_obj.write('\n')


def write_dict(value, base_indent):


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
        f.write(

"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from populus import migrations


class Migration(migrations.Migration):

    migration_id = '0001_initial'
    dependencies = []

    operations = [
        migrations.DeployContract('Thrower'),
    ]

    contract_data = {
        'Thrower': {
            'code': "0x606060405260405160208060318339506080604052518015601e576002565b50600680602b6000396000f3606060405200",
            'code_runtime': "0x606060405200",
            'abi': [
                {
                    "inputs": [{"name": "shouldThrow", "type": "bool"}],
                    "type": "constructor",
                },
            ],
        },
    }
"""
