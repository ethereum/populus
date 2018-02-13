import pprint
import os

from .base import (
    BaseCompilerBackend,
)


class VyperBackend(BaseCompilerBackend):
    project_source_glob = ('*.v.py', '*.vy')
    test_source_glob = ('test_*.v.py', 'test_*.vy')

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        try:
            from vyper import compiler
        except ImportError:
            raise ImportError(
                'vyper needs to be installed to use VyperBackend' +
                ' as compiler backend.'
            )

        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        compiled_contracts = []

        for contract_path in source_file_paths:
            code = open(contract_path).read()
            abi = compiler.mk_full_signature(code)
            bytecode = '0x' + compiler.compile(code).hex()
            bytecode_runtime = '0x' + compiler.compile(code, bytecode_runtime=True).hex()
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
