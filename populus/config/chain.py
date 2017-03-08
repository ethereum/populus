from populus.utils.module_loading import (
    import_string,
)
from populus.utils.types import (
    is_string,
)
from populus.utils.config import (
    ClassImportPath,
)

from .base import Config
from .web3 import Web3Config


CHAIN_IDENTIFIER_MAP = {
    'local': 'populus.chain.geth.LocalGethChain',
    'external': 'populus.chain.external.ExternalChain',
    'tester': 'populus.chain.tester.TesterChain',
    'testrpc': 'populus.chain.testrpc.TestRPCChain',
    'temp': 'populus.chain.geth.TemporaryGethChain',
    'mainnet': 'populus.chain.geth.MainnetChain',
    'testnet': 'populus.chain.geth.TestnetChain',
    'ropsten': 'populus.chain.geth.TestnetChain',
}


UNSUPPORTED_CHAIN_IDENTIFIER_MSG = (
    "Unsupported chain identifier: '{0}'. Must be either a chain class, a dot "
    "separated python path to a chain class, or one of `local`, `external`, "
    "`tester`, `testrpc`, `temp`, `mainnet`, `testnet`, or `ropsten`"
)


class ChainConfig(Config):
    chain_class = ClassImportPath('chain.class')

    def get_chain(self, project, chain_name):
        return self.chain_class(project, chain_name, self)

    def set_chain_class(self, chain_identifier):
        if isinstance(chain_identifier, type):
            self.chain_class = chain_identifier
        elif is_string(chain_identifier):
            if chain_identifier.lower() in CHAIN_IDENTIFIER_MAP:
                self.chain_class = CHAIN_IDENTIFIER_MAP[chain_identifier.lower()]
            else:
                try:
                    import_string(chain_identifier)
                except ImportError:
                    raise ValueError(UNSUPPORTED_CHAIN_IDENTIFIER_MSG.format(chain_identifier))
                else:
                    self.chain_class = chain_identifier
        else:
            raise ValueError(UNSUPPORTED_CHAIN_IDENTIFIER_MSG.format(chain_identifier))

    def get_web3_config(self):
        return self.get_config('web3', config_class=Web3Config)

    @property
    def registrar(self):
        return self['registrar']

    @registrar.setter
    def registrar(self, value):
        self['registrar'] = value

    @property
    def is_external(self):
        from populus.chain import ExternalChain
        return self.chain_class is ExternalChain
