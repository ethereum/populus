import os
import hashlib

from populus.utils.filesystem import (
    get_contracts_dir,
    get_build_dir,
    get_compiled_contracts_file_path,
    get_blockchains_dir,
)
from populus.utils.config import (
    load_config,
    get_config_paths,
)
from populus.compilation import (
    find_project_contracts,
    compile_project_contracts,
)


class Project(object):
    config = None

    def __init__(self, config=None):
        if config is None:
            config = load_config(get_config_paths(os.getcwd()))

        self.config = config

    @property
    def project_dir(self):
        try:
            return self.config['populus']['project_dir']
        except KeyError:
            return os.getcwd()

    @property
    def contracts_dir(self):
        return get_contracts_dir(self.project_dir)

    @property
    def build_dir(self):
        return get_build_dir(self.project_dir)

    @property
    def compiled_contracts_file_path(self):
        return get_compiled_contracts_file_path(self.project_dir)

    @property
    def blockchains_dir(self):
        return get_blockchains_dir(self.project_dir)

    _cached_compiled_contracts_hash = None
    _cached_compiled_contracts = None

    @property
    def compiled_contracts(self):
        source_file_paths = find_project_contracts(self.project_dir)
        source_hash = hashlib.md5(b''.join(
            open(source_file_path, 'rb').read()
            for source_file_path
            in source_file_paths
        )).hexdigest()

        if self._cached_compiled_contracts_hash != source_hash:
            self._cached_compiled_contracts_hash = source_hash
            _, self._cached_compiled_contracts = compile_project_contracts(
                project_dir=self.project_dir,
            )
        return self._cached_compiled_contracts
