
from .backends.solc_auto import (
    get_solc_backend_class_for_version,
)

def compile_lockfile(lockfile):

    pass


def compile_contract_from_source(source, settings,solc_use_version="latest"):

    #TODO move to solcjs useVersion

    compiler_backend = get_solc_backend_class_for_version(solc_use_version)

    pass

