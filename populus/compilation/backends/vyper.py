import pprint
import os

from .base import (
    BaseCompilerBackend,
)
from collections import OrderedDict


class VyperBackend(BaseCompilerBackend):
    project_source_glob = ('*.v.py', '*.vy')
    test_source_glob = ('test_*.v.py', 'test_*.vy')

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        try:
            from vyper import compile_codes
        except ImportError:
            raise ImportError(
                'vyper > 0.1.0b5 needs to be installed to use VyperBackend' +
                ' as compiler backend.'
            )

        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        codes = OrderedDict()
        for contract_path in source_file_paths:
            codes[contract_path] = open(contract_path).read()

        compiled_contracts = []
        formats = ['abi', 'bytecode', 'bytecode_runtime']
        for contract_path, c_info in compile_codes(codes, formats, 'dict').items():
            c_info.update({
                'name': os.path.basename(contract_path).split('.')[0],
                'linkrefs': [],
                'linkrefs_runtime': [],
                'source_path': contract_path
            })
            compiled_contracts.append(c_info)

        return compiled_contracts
