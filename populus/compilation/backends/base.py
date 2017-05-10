import logging

from populus.utils.module_loading import (
    get_import_path,
)


class BaseCompilerBackend(object):
    compiler_settings = None

    def __init__(self, settings):
        self.compiler_settings = settings
        self.logger = logging.getLogger(get_import_path(type(self)))

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        raise NotImplementedError("Must be implemented by subclasses")
