from populus.migrations.registrar import (
    get_registrar,
)

from populus.utils.functional import (
    cached_property,
)

from .base import (
    BaseChain,
)


class ExternalChain(BaseChain):
    """
    Chain class to represent an externally running blockchain that is not
    locally managed.  This class only houses a pre-configured web3 instance.
    """
    @property
    def has_registrar(self):
        return 'registrar' in self.config

    @cached_property
    def registrar(self):
        if not self.has_registrar:
            raise KeyError(
                "The configuration for the {0} chain does not include a "
                "registrar.  Please set this value to the address of the "
                "deployed registrar contract.".format(self.chain_name)
            )
        return get_registrar(
            self.web3,
            address=self.config['registrar'],
        )
