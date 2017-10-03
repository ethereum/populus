import copy
import os
import shutil
import itertools
import warnings
from eth_utils import (
    to_tuple,
)

from populus.config.defaults import (
    load_default_config,
)

from populus.exceptions import (
    PopulusResourceWarning,
)

from populus.compilation import (
    compile_project_contracts,
)

from populus.config import (
    ChainConfig,
    CompilerConfig,
    Config,
    load_config as _load_config,
    load_config_schema,
    write_config,
)

from populus.config.defaults import (
    get_default_config_path,
    get_user_default_config_path,
)

from populus.config.helpers import (
    check_if_user_json_config_file_exists,
    get_user_json_config_file_path,
)

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)

from populus.utils.compile import (
    get_build_asset_dir,
    get_compiled_contracts_asset_path,
    get_contracts_source_dirs,
    get_project_source_paths,
    get_test_source_paths,
)

from populus.utils.filesystem import (
    ensure_path_exists,
    get_latest_mtime,
)

from populus.config.helpers import (
    get_json_config_file_path,
    get_legacy_json_config_file_path,
)

from populus.utils.testing import (
    get_tests_dir,
)


class Project(object):

    project_dir = None
    config_file_path = None
    user_config_file_path = None
    legacy_config_path = None

    def __init__(self, project_dir=None, user_config_file_path=None, create_config_file=False):  # noqa: E501

        self._reset_configs_cache()
        if project_dir is None:
            self.project_dir = os.getcwd()
        else:
            self.project_dir = os.path.abspath(project_dir)

        # user config
        self.user_config_file_path = user_config_file_path
        if self.user_config_file_path is None:
            self.user_config_file_path = get_user_json_config_file_path()
            if not check_if_user_json_config_file_exists():
                user_config_path = get_user_json_config_file_path()
                user_defaults_path = get_user_default_config_path()
                ensure_path_exists(os.path.dirname(user_config_path))
                shutil.copyfile(
                    user_defaults_path,
                    user_config_path
                )

        # legacy config
        legacy_path = get_legacy_json_config_file_path(self.project_dir)
        if os.path.exists(legacy_path):
            self.legacy_config_path = legacy_path
            warnings.warn(
                "Found legacy config file at {legacy_path}".format(
                    legacy_path=legacy_path
                ),
                PopulusResourceWarning
            )

        # project config
        self.config_file_path = get_json_config_file_path(self.project_dir)
        if not os.path.exists(self.config_file_path):
            if create_config_file:
                defaults_path = get_default_config_path()
                shutil.copyfile(defaults_path, self.config_file_path)
            else:
                if self.legacy_config_path is not None:
                    msg = "No project config file found at {project_dir}, but a legacy config exists. Try to upgrade"  # noqa: E501
                else:
                    msg = "No project config file found at {project_dir}"
                raise FileNotFoundError(
                    msg.format(project_dir=self.project_dir)
                )

        self.load_config()

    #
    # Config
    #

    _project_config = None
    _user_config = None
    _config_schema = None

    def load_config(self):
        self._reset_configs_cache()
        self._project_config = _load_config(self.config_file_path)
        self._user_config = _load_config(self.user_config_file_path)

        config_version = self._project_config['version']
        self._config_schema = load_config_schema(config_version)

    def _reset_configs_cache(self):
        self._merged_config_cache = None
        self._user_config_cache = None
        self._project_config_cache = None

    def reload_config(self):
        self.load_config()

    @property
    def user_config(self):

        if self._user_config_cache is None:
            user_config = Config(
                config=self._user_config,
                schema=self._config_schema,
            )
            user_config.unref()
            self._user_config_cache = user_config
            self.merge_user_and_project_configs(user_config, self.project_config)

        return self._user_config_cache

    @property
    def project_config(self):
        if self._project_config_cache is None:
            project_config = Config(
                config=self._project_config,
                parent=Config(self._user_config)
            )
            project_config.unref()
            self._project_config_cache = project_config

            # schema validation
            # partial project config must be merged to get the entire schema
            self.merge_user_and_project_configs(self.user_config, project_config)

        return self._project_config_cache

    def merge_user_and_project_configs(self, user_config, project_config):
        if self._merged_config_cache is None:
            merged_config = copy.deepcopy(self.user_config)
            for key, value in self.project_config.items(flatten=True):
                if key != 'version':
                    merged_config[key] = value
            Config(config=merged_config, schema=self._config_schema)
            self._merged_config_cache = merged_config

        return self._merged_config_cache

    @property
    def config(self):

        return self.merge_user_and_project_configs(self.user_config, self.project_config)

    @config.setter
    def config(self, value):
        if isinstance(value, Config):
            self._merged_config_cache = value
        else:
            self._merged_config_cache = Config(
                config=value,
                schema=self._config_schema
            )

    def clean_config(self):

        items = self.project_config.items(flatten=True)

        default_config = Config(load_default_config(version=self.project_config['version']))
        default_config.unref()
        default_project_keys = [x[0] for x in default_config.items(flatten=True)]

        for key, value in items:
            if self.user_config.get(key) == value and key not in default_project_keys:
                self.project_config.pop(key)

        write_config(self.project_config, self.config_file_path)

    #
    # Project
    #
    @property
    def tests_dir(self):
        return get_tests_dir(self.project_dir)

    #
    # Contracts
    #
    @property
    def compiled_contracts_asset_path(self):
        return get_compiled_contracts_asset_path(self.build_asset_dir)

    @property
    def contracts_source_dir(self):
        warnings.warn(DeprecationWarning(
            "project.contracts_source_dir has been replaced by the plural, "
            "project.contracts_source_dirs which is an iterable of all source "
            "directories populus will search for contracts.  Please update your "
            "code accordingly as this API will be removed in a future release"
        ))
        return self.config.get(
            'compilation.contracts_source_dir',
            get_contracts_source_dirs(self.project_dir),
        )[0]

    @property
    @to_tuple
    def contracts_source_dirs(self):
        source_dirs = self.config.get('compilation.contracts_source_dirs')
        if source_dirs:
            return [os.path.join(self.project_dir, contracts_dir) for contracts_dir in source_dirs]
        else:
            return get_contracts_source_dirs(self.project_dir)

    @property
    def build_asset_dir(self):
        return get_build_asset_dir(self.project_dir)

    _cached_compiled_contracts_mtime = None
    _cached_compiled_contracts = None

    def get_all_source_file_paths(self):
        return tuple(itertools.chain(
            get_project_source_paths(self.contracts_source_dir),
            get_test_source_paths(self.tests_dir),
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
            source_file_paths, compiled_contracts = compile_project_contracts(self)
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

    #
    # Local Blockchains
    #
    def get_chain_config(self, chain_name):
        chain_config_key = 'chains.{chain_name}'.format(chain_name=chain_name)

        if chain_config_key in self.config:
            return self.config.get_config(chain_config_key, config_class=ChainConfig)
        else:
            raise KeyError(
                "Unknown chain: {0!r} - Must be one of {1!r}".format(
                    chain_name,
                    sorted(self.config.get('chains', {}).keys()),
                )
            )

    def get_chain(self, chain_name, chain_config=None):
        """
        Returns a context manager that runs a chain within the context of the
        current populus project.

        Alternatively you can specify any chain name that is present in the
        `chains` configuration key.
        """
        if chain_config is None:
            chain_config = self.get_chain_config(chain_name)
        chain = chain_config.get_chain(self, chain_name)
        return chain

    @property
    def base_blockchain_storage_dir(self):
        return get_base_blockchain_storage_dir(self.project_dir)
