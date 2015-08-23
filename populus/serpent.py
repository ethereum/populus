import os
import hashlib
import subprocess
import contextlib
import re


@contextlib.contextmanager
def cd(path):
    cwd = os.getcwd()

    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(cwd)


class SerpentCompileError(Exception):
    pass


def get_signature(source=None, input_file=None):
    if source and input_file:
        raise ValueError("`source` and `input_file` are mutually exclusive")
    elif source is None and input_file is None:
        raise ValueError("Must provide either `source` or `input_file`")

    command = ['serpent']

    if source:
        cd_path = os.getcwd()
        command.extend(('-s', 'mk_signature'))
    else:
        cd_path = os.path.dirname(input_file) or '.'
        input_file_name = os.path.basename(input_file)
        command.extend(('mk_signature', input_file_name))

    with cd(cd_path):
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        if source:
            stdoutdata, stderrdata = p.communicate(input=source)
        else:
            stdoutdata, stderrdata = p.communicate()

    if p.returncode:
        raise SerpentCompileError('compilation failed')

    signature = stdoutdata.strip()
    return signature


signature_regex = re.compile(
    "^"
    "extern "
    "[^:]+: "  # filename
    "\[(?P<functions>.+)\]"  # functions
    "$"
)


def function_signature_to_abi(func_signature):
    fn_name, raw_inputs, raw_outputs = func_signature.split(':')
    inputs = raw_inputs.strip('[]').split(',')
    outputs = raw_outputs.split(',')
    return {
        "constant": False,
        "type": "function",
        "name": fn_name,
        "inputs": [
            {"name": "arg_{i}".format(i=idx), "type": value}
            for idx, value in enumerate(inputs)
        ],
        "outputs": [
            {"name": "ret_{i}".format(i=idx), "type": value}
            for idx, value in enumerate(outputs)
        ],
    }


def generate_abi(signature):
    functions = signature_regex.match(signature).groups()[0].split(',')
    return [
        function_signature_to_abi(function_signature)
        for function_signature in functions
    ]


def serpent(source=None, input_file=None, raw=False, rich=True):
    if source and input_file:
        raise ValueError("`source` and `input_file` are mutually exclusive")
    elif source is None and input_file is None:
        raise ValueError("Must provide either `source` or `input_file`")

    command = ['serpent']

    if source:
        command.extend(('-s', 'compile'))
    else:
        command.extend(('compile', input_file))

    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    if source:
        stdoutdata, stderrdata = p.communicate(input=source)
    else:
        stdoutdata, stderrdata = p.communicate()

    if p.returncode:
        raise SerpentCompileError('compilation failed')

    code = stdoutdata.strip()
    if raw:
        return code

    if source:
        contract_name = "Unknown-{0}".format(hashlib.md5(code).hexdigest())
    else:
        contract_name, _, _ = input_file.partition('.')

    #`return [
    #`    (contract_name, {
    #`        'natspec-user': {'methods': {}},
    #`        'binary': code,
    #`        'json-abi': [{'inputs': [], 'type': 'constructor'}], 'sol-abi': 'contract Example{function Example();}', 'natspec-dev': {'methods': {}}})]

    #`if not rich:
