import json
import os
import pprint
import subprocess

from .base import (
    BaseCompilerBackend,
)
from populus.utils.filesystem import (
    is_executable_available
)


# FIXME: move where appropriate - separate package if needed.
class LLLCompiler(object):
    """ TODO """
    def __init__(self):
        self.lllc_binary = os.environ.get('LLLC_BINARY', 'lllc')
        if not is_executable_available(self.lllc_binary):
            raise FileNotFoundError("lllc compiler executable not found!")
        return

    def compile(self, code):
        """ Passes an LLL program to the ``lllc`` compiler. """
        proc = subprocess.Popen([self.lllc_binary, '-x'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdoutdata, stderrdata = proc.communicate(code)
        return stdoutdata.rstrip()

    def strip(self, bytecode):
        """ Strips compiler-given bytecode of parts that will not be present at runtime. """

        # remove deployment code: head up to (and including)
        # ``PUSH1 0x00 CODECOPY PUSH1 0x00 RETURN STOP``
        res = bytecode.split('6000396000f300', maxsplit=1)
        nohead = res[-1]
        if nohead == bytecode:
            return ''

        # remove deployment data: tail from (but not including) NIH-marker ``STOP STOP STOP``
        res = nohead.rsplit('000000', maxsplit=1)
        notail = res[0] + '000000'
        return notail


class LLLBackend(BaseCompilerBackend):
    project_source_glob = ('*.lll')
    test_source_glob = ('test_*.lll')

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        compiler  = LLLCompiler()

        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        compiled_contracts = []

        for contract_path in source_file_paths:
            code = open(contract_path).read()
            try:
                with open(contract_path + '.abi') as jsonabi:
                    abi = json.load(jsonabi)
            except FileNotFoundError as e:
                self.logger.error(".lll files require an accompanying .lll.abi JSON ABI file!")
                raise e

            bytecode = '0x' + compiler.compile(code)
            bytecode_runtime = '0x' + compiler.strip(bytecode)

            compiled_contracts.append({
                'name': os.path.basename(contract_path).split('.')[0],
                'abi': abi,
                'bytecode': bytecode,
                'bytecode_runtime': bytecode_runtime,
                'linkrefs': [],
                'linkrefs_runtime': [],
                'source_path': contract_path
            })

        return compiled_contracts
