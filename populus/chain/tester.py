from .base import (
    BaseChain,
)


class TesterChain(BaseChain):
    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        self._running = True

        self.rpc_methods = self.web3.currentProvider.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        self.rpc_methods = self.web3.currentProvider.rpc_methods

        return self
