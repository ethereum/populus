import os
import itertools
import warnings

from populus.compilation import (
    compile_project_contracts,
)
from populus.config import (
    ChainConfig,
    Config,
    get_default_config_path,
    load_config as _load_config,
    load_config_schema,
    write_config as _write_config,
)
from populus.legacy.config import (
    check_if_ini_config_file_exists,
)

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.compile import (
    get_build_asset_dir,
    get_compiled_contracts_asset_path,
    get_contracts_source_dir,
    get_project_source_paths,
    get_test_source_paths,
)
from populus.utils.filesystem import (
    relpath,
)
from populus.utils.config import (
    check_if_json_config_file_exists,
    get_default_project_config_file_path,
    get_json_config_file_path,
)
from populus.utils.geth import (
    get_chaindata_dir,
    get_dapp_dir,
    get_data_dir,
    get_geth_ipc_path,
    get_nodekey_path,
)
from populus.utils.testing import (
    get_tests_dir,
)


class Project(object):
    def __init__(self, config_file_path=None):
        self.config_file_path = config_file_path
        self.load_config()

    #
    # Config
    #
    config_file_path = None

    _project_config = None
    _project_config_schema = None

    def write_config(self):
        if self.config_file_path is None:
            config_file_path = get_default_project_config_file_path(self.project_dir)
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

        if self.config_file_path is None:
            has_ini_config = check_if_ini_config_file_exists()
            has_json_config = check_if_json_config_file_exists()

            if has_ini_config and has_json_config:
                raise DeprecationWarning(
                    "Found both `populus.ini` and `populus.json` config files. "
                    "Please migrate you `populus.ini` file settings into the "
                    "`populus.json` file and remove the `populus.ini` file"
                )
            elif has_ini_config:
                warnings.warn(DeprecationWarning(
                    "The `populus.ini` configuration format has been "
                    "deprecated.  You must upgrade your configuration file to "
                    "the new `populus.json` format."
                ))
                path_to_load = get_default_config_path()
            elif has_json_config:
                path_to_load = get_json_config_file_path()
            else:
                path_to_load = get_default_config_path()
        else:
            path_to_load = self.config_file_path

        self._project_config = _load_config(path_to_load)

        config_version = self._project_config['version']
        self._project_config_schema = load_config_schema(config_version)

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
            self._config_cache = Config
        else:
            self._project_config = value
            config_version = self._project_config['version']
            self._project_config_schema = load_config_schema(config_version)
            self._config_cache = Config(
                config=self._project_config,
                schema=self._project_config_schema,
            )

    #
    # Project
    #
    @property
    def project_dir(self):
        return self.config.get('populus.project_dir', os.getcwd())

    @property
    @relpath
    def tests_dir(self):
        return get_tests_dir(self.project_dir)

    #
    # Contracts
    #
    @property
    @relpath
    def compiled_contracts_asset_path(self):
        return get_compiled_contracts_asset_path(self.build_asset_dir)

    @property
    def compiled_contracts_file_path(self):
        warnings.warn(DeprecationWarning(
            "The `compiled_contracts_file_path` property has been renamed to "
            "`compiled_contracts_asset_path`.  Please update your code to use "
            "this property.  The `compiled_contracts_file_path` property will "
            "be removed in subsequent releases"
        ))
        return self.compiled_contracts_asset_path

    @property
    @relpath
    def contracts_source_dir(self):
        if 'compilation.contracts_dir' in self.config:
            return self.config['compilation.contracts_dir']
        else:
            return get_contracts_source_dir(self.project_dir)

    @property
    @relpath
    def contracts_dir(self):
        warnings.warn(DeprecationWarning(
            "The `contracts_dir` property has been renamed to "
            "`contracts_source_dir`.  Please update your code to use "
            "this property.  The `contracts_dir` property will be removed in "
            "subsequent releases"
        ))
        return self.contracts_source_dir

    @property
    @relpath
    def build_asset_dir(self):
        if 'compilation.build_dir' in self.config:
            return self.config['compilation.build_dir']
        else:
            return get_build_asset_dir(self.project_dir)

    @property
    def build_dir(self):
        warnings.warn(DeprecationWarning(
            "The `contracts_dir` property has been renamed to "
            "`contracts_source_dir`.  Please update your code to use "
            "this property.  The `contracts_dir` property will be removed in "
            "subsequent releases"
        ))
        return self.build_asset_dir

    _cached_compiled_contracts_mtime = None
    _cached_compiled_contracts = None

    def get_source_modification_time(self):
        all_source_paths = tuple(itertools.chain(
            get_project_source_paths(self.contracts_source_dir),
            get_test_source_paths(self.tests_dir),
        ))
        return max(
            os.path.getmtime(source_file_path)
            for source_file_path
            in all_source_paths
        ) if len(all_source_paths) > 0 else None

    def is_compiled_contract_cache_stale(self):
        if self._cached_compiled_contracts is None:
            return True

        source_mtime = self.get_source_modification_time()

        if source_mtime is None:
            return True
        elif self._cached_compiled_contracts_mtime is None:
            return True
        else:
            return self._cached_compiled_contracts_mtime < source_mtime

    def fill_contracts_cache(self, contracts, contracts_mtime):
        """
        :param contracts: become the Project's cache for compiled contracts
        :param contracts_mtime: last modification of supplied contracts
        :return:
        """
        self._cached_compiled_contracts_mtime = contracts_mtime
        self._cached_compiled_contracts = contracts

    @property
    def compiled_contract_data(self):
        if self.is_compiled_contract_cache_stale():
            self._cached_compiled_contracts_mtime = self.get_source_modification_time()
            _, self._cached_compiled_contracts = compile_project_contracts(
                project=self,
                compiler_settings=self.config.get('compilation.settings'),
            )
        return self._cached_compiled_contracts

    @property
    def compiled_contracts(self):
        warnings.warn(DeprecationWarning(
            "The `compiled_contracts` property has been renamed to "
            "`compiled_contract_data`.  Please update your code to use "
            "this property.  The `compiled_contracts` property will be removed in "
            "subsequent releases"
        ))
        return self.compiled_contract_data

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
    @relpath
    def base_blockchain_storage_dir(self):
        return get_base_blockchain_storage_dir(self.project_dir)

    @property
    def blockchains_dir(self):
        warnings.warn(DeprecationWarning(
            "The `blockchains_dir` property has been renamed to "
            "`base_blockchain_storage_dir`.  Please update your code as the "
            "`blockchains_dir` property will be removed in subsequent releases"
        ))
        return self.base_blockchain_storage_dir

    @relpath
    def get_blockchain_data_dir(self, chain_name):
        warnings.warn(DeprecationWarning(
            "The `get_blockchain_data_dir` function has been deprecated and "
            "will be removed in subsequent releases"
        ))
        return get_data_dir(self.project_dir, chain_name)

    @relpath
    def get_blockchain_chaindata_dir(self, chain_name):
        warnings.warn(DeprecationWarning(
            "The `get_blockchain_chaindata_dir` function has been deprecated and "
            "will be removed in subsequent releases"
        ))
        return get_chaindata_dir(self.get_blockchain_data_dir(chain_name))

    @relpath
    def get_blockchain_dapp_dir(self, chain_name):
        warnings.warn(DeprecationWarning(
            "The `get_blockchain_dapp_dir` function has been deprecated and "
            "will be removed in subsequent releases"
        ))
        return get_dapp_dir(self.get_blockchain_data_dir(chain_name))

    @relpath
    def get_blockchain_ipc_path(self, chain_name):
        warnings.warn(DeprecationWarning(
            "The `get_blockchain_ipc_path` function has been deprecated and "
            "will be removed in subsequent releases"
        ))
        return get_geth_ipc_path(self.get_blockchain_data_dir(chain_name))

    @relpath
    def get_blockchain_nodekey_path(self, chain_name):
        warnings.warn(DeprecationWarning(
            "The `get_blockchain_nodekey_path` function has been deprecated and "
            "will be removed in subsequent releases"
        ))
        return get_nodekey_path(self.get_blockchain_data_dir(chain_name))
