from .base import (
    Chain,
)


class TesterChain(Chain):
    #
    # TestRPC Proxy Methods
    #
    def full_reset(self, *args, **kwargs):
        return self.rpc_methods.full_reset(*args, **kwargs)

    def reset(self, *args, **kwargs):
        return self.rpc_methods.evm_reset(*args, **kwargs)

    def snapshot(self, *args, **kwargs):
        return int(self.rpc_methods.evm_snapshot(*args, **kwargs), 16)

    def revert(self, *args, **kwargs):
        return self.rpc_methods.evm_revert(*args, **kwargs)

    def mine(self, *args, **kwargs):
        return self.rpc_methods.evm_mine(*args, **kwargs)

    def configure(self, *args, **kwargs):
        return self.rpc_methods.rpc_configure(*args, **kwargs)

    _running = False

    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        self.rpc_methods = self.web3.currentProvider.rpc_methods

        self.full_reset()
        self.configure('eth_mining', False)
        self.configure('eth_protocolVersion', '0x3f')
        self.configure('net_version', 1)
        self.mine()

        self._running = True
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        self._running = False
