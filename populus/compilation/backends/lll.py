from .base import (
    BaseCompilerBackend,
)


class LLLBackend(BaseCompilerBackend):
    project_source_glob = ('*.lll')
    test_source_glob = ('test_*.lll.py')

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        try:
            raise Exception # TODO: check for binary
        except ImportError:
            raise ImportError(
                'lllc needs to be installed to use LLLBackend as compiler backend.'
            )

        self.logger.debug("Compiler Settings: %s", pprint.pformat(self.compiler_settings))

        compiled_contracts = []

        # TODO: boilerplate from ViperBackend - move up?
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
