import os

from populus.utils.filesystem import (
    get_contracts_dir,
    get_build_dir,
    get_compiled_contracts_file_path,
    get_blockchains_dir,
)


class Project(object):
    config = None

    def __init__(self, config):
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
