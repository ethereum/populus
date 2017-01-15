import copy

from populus.utils.networking import (
    get_open_port,
    wait_for_connection,
)

from .base import (
    Chain,
)


class TestRPCChain(Chain):
    provider = None
    rpc_port = None

    #
    # Web3 API
    #
    def get_web3_config(self):
        web3_config = copy.deepcopy(super(TestRPCChain, self).get_web3_config())
        web3_config.setdefault('provider.settings.rpc_port', self.rpc_port)
        return web3_config

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

        self._running = True

        self.rpc_port = get_open_port()

        self.provider = self.web3.currentProvider
        self.rpc_methods = self.provider.server.application.rpc_methods

        self.full_reset()
        self.configure('eth_mining', False)
        self.configure('eth_protocolVersion', '0x3f')
        self.configure('net_version', 1)
        self.mine()

        wait_for_connection('127.0.0.1', self.rpc_port)
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.provider.server.stop()
            self.provider.server.close()
            self.provider.thread.kill()
        except AttributeError:
            self.provider.server.shutdown()
        finally:
            self._running = False
