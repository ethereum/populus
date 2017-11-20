import logging
import os

from eth_utils import (
    to_tuple,
)
from populus.utils.module_loading import (
    get_import_path,
)
from populus.utils.filesystem import (
    recursive_find_files,
)


class BaseCompilerBackend(object):
    compiler_settings = None
    project_source_extensions = None
    test_source_extensions = None

    def __init__(self, settings):
        self.compiler_settings = settings
        self.logger = logging.getLogger(get_import_path(type(self)))

    def get_compiled_contracts(self, source_file_paths, import_remappings):
        raise NotImplementedError("Must be implemented by subclasses")

    @to_tuple
    def _find_source_files(self, base_dir, extensions):
        return (
            os.path.relpath(source_file_path)
            for source_file_path
            in recursive_find_files(base_dir, extensions)
        )

    def get_project_source_paths(self, contracts_source_dir):
        return self._find_source_files(contracts_source_dir, self.project_source_extensions)

    def get_test_source_paths(self, tests_dir):
        return self._find_source_files(tests_dir, self.test_source_extensions)
