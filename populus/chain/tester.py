from .base import (
    BaseChain,
)


class TesterChain(BaseChain):
    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        self._running = True

        self.eth_tester = self.web3.providers[0].ethereum_tester
        self.eth_tester.reset_to_genesis()
        # self.eth_tester.disable_auto_mine_transactions()
        # self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        # self.rpc_methods.rpc_configure('net_version', 1)
        # self.eth_tester.mine_blocks()

        return self
