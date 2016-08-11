import os
import hashlib

from web3 import Web3
from web3.providers.rpc import (
    TestRPCProvider,
)

from populus.utils.networking import (
    get_open_port,
)
from populus.utils.filesystem import (
    get_contracts_dir,
    get_build_dir,
    get_compiled_contracts_file_path,
    get_blockchains_dir,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.contracts import (
    package_contracts,
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

    def __init__(self, config=None, chain=None):
        if config is None:
            config = load_config(get_config_paths(os.getcwd()))

        self.config = config

        if chain is None and self.config.has_option('populus', 'default_chain'):
            chain = self.config.get('populus', 'default_chain')

        self.chain = chain

    @property
    def project_dir(self):
        if self.config.has_option('populus', 'project_dir'):
            return self.config.get('populus', 'project_dir')
        else:
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

    @property
    def web3(self):
        if self.chain is None:
            raise AttributeError(
                "To access the `web3` property the `project.chain` attribute "
                "must be set to a valid chain name from your `populus.ini` "
                "configuration file, or to one of the preset public chain names "
                "(mainnet/morden)"
            )
        elif self.chain not in self.config.chains:
            # TODO: lookup whether this is a local chain.
            raise KeyError(
                "Unknown chain. given: {0!r}  expected one of: {1!r}".format(
                    self.chain,
                    self.config.chains.keys(),
                )
            )

        chain_config = self.config.chains[self.chain]

        try:
            provider_import_path = chain_config['provider']
        except KeyError:
            # TODO: lookup whether this is a local chain and default to IPC
            # provider with the local project chain ipc_path.
            raise KeyError("Chain configurations must declare a provider")

        ProviderClass = import_string(provider_import_path)
        provider_kwargs = {
            key: value
            for key, value in chain_config.items()
            if key != 'provider'
        }

        if issubclass(ProviderClass, TestRPCProvider):
            provider_kwargs.setdefault('port', get_open_port())

        provider = ProviderClass(**provider_kwargs)
        return Web3(provider)

    @property
    def contract_factories(self):
        return package_contracts(self.web3, self.compiled_contracts)
