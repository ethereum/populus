from __future__ import absolute_import

from eth_utils import (
    is_string,
)

from web3 import Web3

from populus.utils.module_loading import (
    import_string,
)
from populus.config.helpers import (
    ClassImportPath,
)

from .base import Config


PROVIDER_IDENTIFIER_MAP = {
    'ipc': 'web3.providers.ipc.IPCProvider',
    'rpc': 'web3.providers.rpc.HTTPProvider',
}


UNSUPPORTED_PROVIDER_IDENTIFIER_MSG = (
    "Unsupported type. Must be either a provider class, a dot "
    "separated python path to a provider class, or one of `ipc` or "
    "`rpc`"
)


class Web3Config(Config):
    provider_class = ClassImportPath('provider.class')

    def set_provider_class(self, provider_identifier):
        if isinstance(provider_identifier, type):
            self.provider_class = provider_identifier
        elif is_string(provider_identifier):
            if provider_identifier.lower() in PROVIDER_IDENTIFIER_MAP:
                self.provider_class = PROVIDER_IDENTIFIER_MAP[provider_identifier.lower()]
            else:
                try:
                    import_string(provider_identifier)
                except ImportError:
                    raise ValueError(
                        UNSUPPORTED_PROVIDER_IDENTIFIER_MSG.format(provider_identifier)
                    )
                else:
                    self.provider_class = provider_identifier
        else:
            raise ValueError(UNSUPPORTED_PROVIDER_IDENTIFIER_MSG.format(provider_identifier))

    @property
    def provider(self):
        return self.provider_class(**self.provider_kwargs)

    @property
    def provider_kwargs(self):
        return self.get('provider.settings', {})

    @provider_kwargs.setter
    def provider_kwargs(self, value):
        self['provider.settings'] = value

    def get_web3(self):
        web3 = Web3(self.provider)

        if 'eth.default_account' in self:
            web3.eth.defaultAccount = self['eth.default_account']

        return web3

    @property
    def default_account(self):
        return self['eth.default_account']

    @default_account.setter
    def default_account(self, value):
        self['eth.default_account'] = value
