
from .backends.solc_auto import (
    get_solc_backend_class_for_version,
)

def compile_lockfile(lockfile):

    pass


def compile_contract_from_source(source_path, settings, import_remappings=None, solc_use_version="latest"):

    #TODO move to solcjs useVersion

    logger = logging.getLogger('populus.compilation.compile_project_contracts')
    if import_remappings == None:
        import_remappings = []

    compiler_backend = get_solc_backend_class_for_version(solc_use_version)
    return compiler_backend.get_compiled_contracts(
        source_file_paths=(source_path,),
        import_remappings=import_remappings,
    )

