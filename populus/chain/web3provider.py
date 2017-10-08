from .base import BaseChain
from web3 import Web3, HTTPProvider, IPCProvider

from populus.utils.functional import (
    cached_property,
)


class BaseWeb3Chain(BaseChain):

    def get_web3_config(self):

        raise NotImplementedError("Direct web3 chains use existing web3 provider")

    def web3_config(self):

        raise NotImplementedError("Direct web3 chains use existing web3 provider")


class Web3HTTPProviderChain(BaseWeb3Chain):

    rpc_path = None

    @cached_property
    def web3(self):
        if not self._running:
            raise ValueError("Chain must be running prior to accessing web3")
        return Web3(HTTPProvider(self.rpc_path))


class Web3IPCProviderChain(BaseWeb3Chain):

    ipc_path = None

    @cached_property
    def web3(self):
        if not self._running:
            raise ValueError("Chain must be running prior to accessing web3")
        return Web3(IPCProvider(self.ipc_path))
