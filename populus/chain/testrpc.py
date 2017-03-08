import copy

from populus.utils.networking import (
    wait_for_connection,
    get_open_port,
)

from .base import (
    BaseChain,
)


class TestRPCChain(BaseChain):
    rpc_port = None

    def get_web3_config(self):
        base_config = super(TestRPCChain, self).get_web3_config()
        config = copy.deepcopy(base_config)
        config['provider.settings.port'] = self.rpc_port
        return config

    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        if self.rpc_port is None:
            self.rpc_port = get_open_port()

        self._running = True

        self.rpc_methods = self.web3.currentProvider.server.application.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        wait_for_connection('127.0.0.1', self.rpc_port)
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.web3.currentProvider.server.stop()
            self.web3.currentProvider.server.close()
            self.web3.currentProvider.thread.kill()
        except AttributeError:
            self.web3.currentProvider.server.shutdown()
            self.web3.currentProvider.server.server_close()
        finally:
            self._running = False
