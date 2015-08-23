import subprocess
import itertools


class CompileError(Exception):
    pass


SOLC_BINARY = 'solc'


def solc(source=None, input_files=None, add_std=True, combined_json='json-abi,binary,sol-abi,natspec-dev,natspec-user'):

    if source and input_files:
        raise ValueError("`source` and `input_files` are mutually exclusive")
    elif source is None and input_files is None:
        raise ValueError("Must provide either `source` or `input_files`")

    command = ['solc']
    if add_std:
        command.append('--add-std=1')

    if combined_json:
        command.extend(('--combined-json', combined_json))

    if input_files:
        command.extend(itertools.chain(*zip(itertools.repeat('--input-file'), input_files)))

    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    if source:
        stdoutdata, stderrdata = p.communicate(input=source)
    else:
        stdoutdata, stderrdata = p.communicate()

    if p.returncode:
        raise CompileError('compilation failed')
    return stdoutdata
