import pprint
import os
import fnmatch

from .base import (
    BaseCompilerBackend,
)


class ViperBackend(BaseCompilerBackend):
    project_source_extensions = ('*.v.py', '*.vy')
    test_source_extensions = ('*.py', )

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        try:
            from viper import compiler
        except ImportError:
            raise Exception('viper needs to be installed to use ViperBackend as compiler backend.')

        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        compiled_contracts = []
        paths = [
            x for x in source_file_paths
            if any([fnmatch.fnmatch(x, p) for p in self.project_source_extensions])
        ]

        for contract_path in paths:
            code = open(contract_path).read()
            abi = compiler.mk_full_signature(code)
            bytecode = '0x' + compiler.compile(code).hex()
            compiled_contracts.append({
                'name': os.path.basename(contract_path).split('.')[0],
                'abi': abi,
                'bytecode': bytecode,
                'linkrefs': [],
                'linkrefs_runtime': [],
                'source_path': contract_path
            })

        return compiled_contracts
