import subprocess
import functools
import yaml
import re

from populus.utils.formatting import (
    add_0x_prefix,
)
from populus.utils.filesystem import (
    is_executable_available,
)


class CompileError(Exception):
    pass


SOLC_BINARY = 'solc'


version_regex = re.compile('Version: ([0-9]+\.[0-9]+\.[0-9]+(-[a-f0-9]+)?)')


is_solc_available = functools.partial(is_executable_available, 'solc')


def solc_version():
    version_string = subprocess.check_output(['solc', '--version'])
    version = version_regex.search(version_string).groups()[0]
    return version


def solc(source=None, input_files=None, add_std=True,
         combined_json='abi,bin,bin-runtime', optimize=True):

    if source and input_files:
        raise ValueError("`source` and `input_files` are mutually exclusive")
    elif source is None and input_files is None:
        raise ValueError("Must provide either `source` or `input_files`")

    command = ['solc']
    if add_std:
        command.append('--add-std')

    if combined_json:
        command.extend(('--combined-json', combined_json))

    if input_files:
        command.extend(input_files)

    if optimize:
        command.append('--optimize')

    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    if source:
        stdoutdata, stderrdata = p.communicate(input=source)
    else:
        stdoutdata, stderrdata = p.communicate()

    if p.returncode:
        raise CompileError('compilation failed: ' + stderrdata)

    contracts = yaml.safe_load(stdoutdata)['contracts']

    for _, data in contracts.items():
        data['abi'] = yaml.safe_load(data['abi'])

    sorted_contracts = sorted(contracts.items(), key=lambda c: c[0])

    return {
        contract_name: {
            'abi': contract_data['abi'],
            'code': add_0x_prefix(contract_data['bin']),
            'code_runtime': add_0x_prefix(contract_data['bin-runtime']),
            'source': source,
        }
        for contract_name, contract_data
        in sorted_contracts
    }
