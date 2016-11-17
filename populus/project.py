import os
import warnings
import json

from populus.utils.filesystem import (
    relpath,
    find_solidity_source_files,
)
from populus.utils.packaging import (
    get_project_package_manifest_path,
    get_installed_packages_dir,
    get_installed_dependency_locations,
)
from populus.utils.config import (
    get_json_config_file_path,
    check_if_json_config_file_exists,
    get_default_project_config_file_path,
)

from populus.utils.contracts import (
    get_contracts_source_dir,
)
from populus.utils.compile import (
    get_build_asset_dir,
    get_compiled_contracts_asset_path,
)
from populus.utils.config import (
    sort_prioritized_configs,
)
from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.functional import (
    cached_property,
    cast_return_to_ordered_dict,
    cast_return_to_dict,
)

from populus.compilation import (
    compile_project_contracts,
)
from populus.config import (
    get_default_config_path,
    load_config as _load_config,
    write_config as _write_config,
    load_config_schema,
    Config,
    ChainConfig,
)
from populus.legacy.config import (
    check_if_ini_config_file_exists,
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
        self._project_config_schema = load_config_schema()

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

    #
    # Project
    #
    @property
    @relpath
    def project_dir(self):
        return self.config.get('populus.project_dir', os.getcwd())

    #
    # Packaging: Manifest
    #
    @property
    def has_package_manifest(self):
        return os.path.exists(self.package_manifest_path)

    @property
    @relpath
    def package_manifest_path(self):
        return get_project_package_manifest_path(self.project_dir)

    @property
    def package_manifest(self):
        with open(self.package_manifest_path) as package_manifest_file:
            return json.load(package_manifest_file)

    #
    # Packaging: Installed Packages
    #
    @property
    def dependencies(self):
        if self.has_package_manifest:
            package_manifest = self.package_manifest
        else:
            package_manifest = {}
        package_dependencies = package_manifest.get('dependencies', {})
        return package_dependencies

    @property
    @relpath
    def installed_packages_dir(self):
        return get_installed_packages_dir(self.project_dir)

    @property
    @cast_return_to_dict
    def installed_package_locations(self):
        # TODO: rename to `installed_dependency_locations`
        return get_installed_dependency_locations(self.installed_packages_dir)

    #
    # Packaging: Backends
    #
    @cast_return_to_ordered_dict
    def get_package_backend_config(self):
        package_backend_config = self.config.get_config('packaging.backends')
        return sort_prioritized_configs(package_backend_config, self.config)

    @cached_property
    @cast_return_to_ordered_dict
    def package_backends(self):
        for backend_name, backend_config in self.get_package_backend_config().items():
            PackageBackendClass = import_string(backend_config['class'])
            yield (
                backend_name,
                PackageBackendClass(
                    self,
                    backend_config.get_config('settings'),
                ),
            )

    #
    # Contract Source and Compilation
    #
    @property
    @relpath
    def contracts_source_dir(self):
        return self.config.get(
            'compilation.contracts_source_dir',
            get_contracts_source_dir(self.project_dir),
        )

    @property
    def contract_source_paths(self):
        return find_solidity_source_files(self.contracts_source_dir)

    @property
    @relpath
    def build_asset_dir(self):
        return get_build_asset_dir(self.project_dir)

    @property
    @relpath
    def compiled_contracts_asset_path(self):
        return get_compiled_contracts_asset_path(self.build_asset_dir)

    @property
    def compiled_contract_data(self):
        # TODO: this should move to the provider.
        if self.is_compiled_contract_cache_stale():
            self._cached_compiled_contracts_mtime = self.get_source_modification_time()
            _, self._cached_compiled_contracts = compile_project_contracts(
                project=self,
                compiler_settings=self.config.get('compilation.settings', {})
            )
        return self._cached_compiled_contracts

    _cached_compiled_contracts_mtime = None
    _cached_compiled_contracts = None

    def get_source_modification_time(self):
        source_file_paths = find_solidity_source_files(
            self.contracts_source_dir,
        )
        return max(
            os.path.getmtime(source_file_path)
            for source_file_path
            in source_file_paths
        ) if len(source_file_paths) > 0 else None

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

        Support pre-configured chain names:

        - 'testrpc': Chain backed by an ephemeral eth-testrpc chain.
        - 'tester': Chain backed by an ephemeral ethereum.tester chain.
        - 'temp': Chain backed by geth running a local chain in a temporary
          directory that will be automatically deleted when the chain shuts down.
        - 'mainnet': Chain backed by geth running against the public mainnet.
        - 'morden': Chain backed by geth running against the public morden
          testnet.

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
