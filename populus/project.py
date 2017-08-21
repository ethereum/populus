import os
import itertools
import sys

from populus.utils.filesystem import (
    is_same_path,
)


from populus.compilation.helpers import (
    get_dir_source_paths,
)

from populus.compilation.compile import (
    compile_dirs,
)

from populus.config import (
    ChainConfig,
    CompilerConfig,
    Config,
    get_default_config_path,
    load_config as _load_config,
    load_project_config_schema,
    write_config as _write_config,
)


from populus.utils.filesystem import (
    relpath,
    get_latest_mtime,
)
from populus.config.helpers import (
    check_if_project_json_file_exists,
    get_project_json_config_file_path,
)


from populus.defaults import (
    BUILD_ASSET_DIR,
    COMPILED_CONTRACTS_ASSET_FILENAME,
    DEFAULT_CONTRACTS_DIR,
    DEFAULT_TESTS_DIR,
    PROJECT_JSON_CONFIG_FILENAME,
    DEPLOY_JSON_CONFIG_FILENAME,

)


class Project(object):

    #
    # Config
    #
    project_root_dir = None

    _project_config = None
    _project_config_schema = None

    def __init__(self, project_root_dir, user_config):
        self.project_root_dir = os.path.abspath(project_root_dir)
        self.user_config = user_config

        if not self.has_json_config():
            raise FileNotFoundError(
                "Did not find config file {file_name} in {dir_name}".format(
                    file_name=PROJECT_JSON_CONFIG_FILENAME, dir_name=self.project_root_dir)
            )
        self.json_config_file_path = os.path.join(
            self.project_root_dir,
            PROJECT_JSON_CONFIG_FILENAME
        )
        self.load_config()

        if not any(is_same_path(p, project_root_dir) for p in sys.path):
            # ensure that the project directory is in the sys.path
            sys.path.insert(0, project_root_dir)

    def has_json_config(self):
        return check_if_project_json_file_exists(self.project_root_dir)

    @property
    def deploy_config_path(self):
        return os.path.join(self.project_root_dir, DEPLOY_JSON_CONFIG_FILENAME)

    def write_config(self):
        if self.config_file_path is None:
            config_file_path = get_project_json_config_file_path(self.project_dir)
        else:
            config_file_path = self.config_file_path

        self.config_file_path = _write_config(
            self.project_dir,
            self.config,
            write_path=config_file_path,
        )

        return self.config_file_path

    def load_config(self):
        self._config_cache = None

        self._project_config = _load_config(self.json_config_file_path)
        self._project_config_schema = load_project_config_schema()

    def reload_config(self):
        self.load_config()

    _config_cache = None

    @property
    def config(self):
        if self._config_cache is None:
            self._config_cache = Config(
                config=self._project_config,
                schema=self._project_config_schema,
            )
        return self._config_cache

    @config.setter
    def config(self, value):
        if isinstance(value, Config):
            self._config_cache = value
        else:
            self._project_config = value
            self._project_config_schema = load_project_config_schema()
            self._config_cache = Config(
                config=self._project_config,
                schema=self._project_config_schema,
            )

    #
    # Project
    #
    @property
    @relpath
    def project_dir(self):
        return self.config.get('populus.project_dir', os.getcwd())

    @property
    def tests_dir(self):
        dir_path = self.config.get(
            'locations.tests_dir',
            DEFAULT_TESTS_DIR
        )

        return os.path.join(self.project_root_dir, dir_path)

    #
    # Contracts
    #
    @property
    def compiled_contracts_asset_path(self):
        return os.path.join(
            self.build_asset_dir,
            COMPILED_CONTRACTS_ASSET_FILENAME,
        )

    @property
    def contracts_source_dir(self):
        dir_path = self.config.get(
            'locations.contracts_source_dir',
            DEFAULT_CONTRACTS_DIR)

        return os.path.join(self.project_root_dir, dir_path)

    @property
    def build_asset_dir(self):
        return os.path.join(self.project_root_dir, BUILD_ASSET_DIR)

    _cached_compiled_contracts_mtime = None
    _cached_compiled_contracts = None

    def get_all_source_file_paths(self):
        return tuple(itertools.chain(
            get_dir_source_paths(self.contracts_source_dir),
            get_dir_source_paths(self.tests_dir),
        ))

    def is_compiled_contract_cache_stale(self):
        if self._cached_compiled_contracts is None:
            return True

        source_mtime = get_latest_mtime(self.get_all_source_file_paths())

        if source_mtime is None:
            return True
        elif self._cached_compiled_contracts_mtime is None:
            return True
        else:
            return self._cached_compiled_contracts_mtime < source_mtime

    def fill_contracts_cache(self, compiled_contracts, contracts_mtime):
        """
        :param contracts: become the Project's cache for compiled contracts
        :param contracts_mtime: last modification of supplied contracts
        :return:
        """
        self._cached_compiled_contracts_mtime = contracts_mtime
        self._cached_compiled_contracts = compiled_contracts

    @property
    def compiled_contract_data(self):
        if self.is_compiled_contract_cache_stale():
            source_file_paths, compiled_contracts = compile_dirs(
                (self.contracts_source_dir, self.tests_dir),
                self.user_config,
                self.config.get('compilation.import_remappings')
            )
            contracts_mtime = get_latest_mtime(source_file_paths)
            self.fill_contracts_cache(
                compiled_contracts=compiled_contracts,
                contracts_mtime=contracts_mtime,
            )
        return self._cached_compiled_contracts

    #
    # Compiler Backend
    #
    def get_compiler_backend(self):
        compilation_config = self.config.get_config(
            'compilation.backend',
            config_class=CompilerConfig,
        )
        return compilation_config.backend