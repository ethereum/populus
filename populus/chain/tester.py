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

        return self
