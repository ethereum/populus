from populus.utils.functional import (
    cached_property,
)
from populus.utils.config import (
    ClassImportPath,
)

from .base import Config
from .web3 import Web3Config


class ChainConfig(Config):
    chain_class = ClassImportPath('chain.class')

    def get_chain(self, project, chain_name):
        return self.chain_class(project, chain_name, self)

    @cached_property
    def web3_config(self):
        return self.get_config('web3', config_class=Web3Config)

    @property
    def registrar(self):
        return self['registrar']

    @registrar.setter
    def registrar(self, value):
        self['registrar'] = value
