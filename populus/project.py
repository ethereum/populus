import os
import hashlib

from web3.utils.string import (
    is_string,
)

from populus.utils.filesystem import (
    get_contracts_dir,
    get_build_dir,
    get_compiled_contracts_file_path,
    get_blockchains_dir,
    get_migrations_dir,
)
from populus.utils.chains import (
    get_data_dir,
    get_chaindata_dir,
    get_geth_ipc_path,
)
from populus.utils.config import (
    load_config,
    get_config_paths,
    PRIMARY_CONFIG_FILENAME,
)
from populus.migrations.migration import (
    sort_migrations,
)
from populus.migrations.loading import (
    find_project_migrations,
    load_project_migrations,
)
from populus.compilation import (
    find_project_contracts,
    compile_project_contracts,
)

from populus.chain import (
    TestRPCChain,
    TemporaryGethChain,
    MordenChain,
    MainnetChain,
    LocalGethChain,
)


class Project(object):

    #: Instance of :class:`populus.utils.Config`, a subclass of ConfigParser
    config = None

    def __init__(self, config_file_paths=None):
        if not config_file_paths:
            config_file_paths = get_config_paths(os.getcwd())
        else:
            self.primary_config_file_path = config_file_paths[0]

        if is_string(config_file_paths):
            config_file_paths = [config_file_paths]

        self.config = load_config(config_file_paths)

    #
    # Config
    #
    _primary_config_file_path = None

    @property
    def primary_config_file_path(self):
        if self._primary_config_file_path is not None:
            return self._primary_config_file_path
        return os.path.join(self.project_dir, PRIMARY_CONFIG_FILENAME)

    @primary_config_file_path.setter
    def primary_config_file_path(self, value):
        self._primary_config_file_path = value

    def write_config(self, destination_path=None):
        if destination_path is None:
            destination_path = self.primary_config_file_path
        with open(destination_path, 'w') as config_file:
            self.config.write(config_file)
        return destination_path

    #
    # Project
    #
    @property
    def project_dir(self):
        if self.config.has_option('populus', 'project_dir'):
            return self.config.get('populus', 'project_dir')
        else:
            return os.getcwd()

    #
    # Contracts
    #
    @property
    def contracts_dir(self):
        return get_contracts_dir(self.project_dir)

    @property
    def build_dir(self):
        if self.config.has_option('populus', 'build_dir'):
            return self.config.get('populus', 'build_dir')
        else:
            return get_build_dir(self.project_dir)

    @property
    def compiled_contracts_file_path(self):
        return get_compiled_contracts_file_path(self.project_dir)

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

    #
    # Local Blockchains
    #
    def get_chain(self, chain_name, *chain_args, **chain_kwargs):
        """
        Returns a context manager that runs a chain within the context of the
        current populus project.

        Support pre-configured chain names:

        - 'testrpc': Chain backed by an ephemeral eth-testrpc chain.
        - 'temp': Chain backed by geth running a local chain in a temporary
          directory that will be automatically deleted when the chain shuts down.
        - 'mainnet': Chain backed by geth running against the public mainnet.
        - 'morden': Chain backed by geth running against the public morden
          testnet.

        Alternatively you can specify any of the pre-configured chains from the
        project's populus.ini configuration file.

        All geth backed chains are subject to up to 10 minutes of wait time
        during first boot to generate the DAG file if the chain configured to
        mine.

        * See https://github.com/ethereum/wiki/wiki/Ethash-DAG
        * These are shared across all Ethereum nodes and live in
          ``$(HOME)/.ethash/`` folder

        To avoid this long wait time, you can manuall pre-generate the DAG with
        ``$ geth makedag 0 $HOME/.ethash``

        Example:

        .. code-block:: python

            >>> from populus.project import default_project as my_project
            >>> with my_project.get_chain('testrpc') as chain:
            ...     web3 = chain.web3
            ...     MyContract = chain.contract_factories.MyContract
            ...     # do things


        :param chain_name: The name of the chain that should be returned
        :param chain_args: Positional arguments that should be passed into the
                           chain constructor.
        :param chain_kwargs: Named arguments that should be passed into the
                             constructor

        :return: :class:`populus.chain.Chain`
        """
        if chain_name == 'testrpc':
            return TestRPCChain(self, 'testrpc', *chain_args, **chain_kwargs)
        elif chain_name == 'temp':
            return TemporaryGethChain(self, 'temp', *chain_args, **chain_kwargs)

        try:
            chain_config = self.config.chains[chain_name]
        except KeyError:
            raise KeyError(
                "Unknown chain: {0!r} - Must be one of {1!r}".format(
                    chain_name,
                    sorted(self.config.chains.keys()),
                )
            )

        combined_kwargs = dict(**chain_config)
        combined_kwargs.update(chain_kwargs)

        if chain_name == 'morden':
            return MordenChain(self, 'morden', *chain_args, **combined_kwargs)
        elif chain_name == 'mainnet':
            return MainnetChain(self, 'mainnet', *chain_args, **combined_kwargs)
        else:
            return LocalGethChain(self,
                                  chain_name=chain_name,
                                  *chain_args,
                                  **chain_kwargs)

    @property
    def blockchains_dir(self):
        return get_blockchains_dir(self.project_dir)

    def get_blockchain_data_dir(self, chain_name):
        return get_data_dir(self.project_dir, chain_name)

    def get_blockchain_chaindata_dir(self, chain_name):
        return get_chaindata_dir(self.get_blockchain_data_dir(chain_name))

    def get_blockchain_ipc_path(self, chain_name):
        return get_geth_ipc_path(self.get_blockchain_data_dir(chain_name))

    #
    # Migrations
    #
    @property
    def migrations_dir(self):
        return get_migrations_dir(self.project_dir)

    @property
    def migration_files(self):
        return list(sorted(find_project_migrations(self.project_dir)))

    @property
    def migrations(self):
        return sort_migrations(
            load_project_migrations(self.project_dir),
            flatten=True,
        )
