import subprocess
import itertools
import functools
import yaml
import re

from populus import utils


class CompileError(Exception):
    pass


SOLC_BINARY = 'solc'


version_regex = re.compile('Version: ([0-9]+\.[0-9]+\.[0-9]+(-[a-f0-9]+)?)')


is_solc_available = functools.partial(utils.is_executable_available, 'solc')


def solc_version():
    version_string = subprocess.check_output(['solc', '--version'])
    version = version_regex.search(version_string).groups()[0]
    return version


def solc(source=None, input_files=None, add_std=True,
         combined_json='abi,bin,devdoc,userdoc',
         raw=False, rich=True, optimize=False):

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
        command.extend(itertools.chain(*zip(itertools.repeat('--input-file'), input_files)))

    if optimize:
        command.append('--optimize')

    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    if source:
        stdoutdata, stderrdata = p.communicate(input=source)
    else:
        stdoutdata, stderrdata = p.communicate()

    if p.returncode:
        raise CompileError('compilation failed')

    if raw:
        return stdoutdata

    contracts = yaml.safe_load(stdoutdata)['contracts']

    for contract_name, data in contracts.items():
        data['abi'] = yaml.safe_load(data['abi'])
        data['devdoc'] = yaml.safe_load(data['devdoc'])
        data['userdoc'] = yaml.safe_load(data['userdoc'])

    sorted_contracts = sorted(contracts.items(), key=lambda c: c[0])

    if not rich:
        return sorted_contracts

    compiler_version = solc_version()

    return {
        contract_name: {
            'code': "0x" + contract['bin'],
            'info': {
                'abiDefinition': contract.get('abi'),
                'compilerVersion': compiler_version,
                'developerDoc': contract.get('devdoc'),
                'language': 'Solidity',
                'languageVersion': '0',
                'source': source,  # what to do for files?
                'userDoc': contract.get('userdoc')
            },
        }
        for contract_name, contract
        in sorted_contracts
    }
