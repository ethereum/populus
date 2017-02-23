from .base import (
    BaseTesterChain,
)


class TesterChain(BaseTesterChain):
    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        self._running = True

        self.provider = self.web3.currentProvider
        self.rpc_methods = self.provider.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        self._running = False
