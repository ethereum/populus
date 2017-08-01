import logging

from populus.utils.module_loading import (
    get_import_path,
)

from semantic_version import (
    Spec,
    Version,
)

from solc import (
    get_solc_version,
)



#TODO-PRIORITY-01:
# move to new global compilation settings
# by solc version

DEFAULT_SOLC_SETTINGS = {
    'optimize': True,
    'output_values': ['abi', 'bin', 'bin-runtime', 'metadata']
}


class BaseCompilerBackend(object):
    compiler_settings = None
    solc_version = None

    def __init__(self, settings=None):

        try:
            assert get_solc_version() in Spec(self.solc_version)
        except AssertionError:
            raise OSError(
                "The 'SolcStandardJSONBackend can only be used with solc versions {version}.".format(
                    version=self.solc_version
                )
            )
        except:
            raise

        self.compiler_settings = DEFAULT_SOLC_SETTINGS if settings == None else settings
        self.logger = logging.getLogger(get_import_path(type(self)))

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        raise NotImplementedError("Must be implemented by subclasses")
