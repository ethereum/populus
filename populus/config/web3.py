from web3 import Web3

from populus.utils.config import (
    ClassImportPath,
)

from .base import Config


class Web3Config(Config):
    provider_class = ClassImportPath('provider.class')

    @property
    def provider(self):
        provider_kwargs = self.get('provider.settings', {})
        return self.provider_class(**provider_kwargs)

    def get_web3(self):
        web3 = Web3(self.provider)

        if 'eth.default_account' in self:
            web3.eth.defaultAccount = self['eth.default_account']

        return web3
