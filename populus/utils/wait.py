import random
import gevent

from web3.providers.rpc import TestRPCProvider

from .empty import empty


def wait_for_transaction_receipt(web3, txn_hash, timeout=120):
    with gevent.Timeout(timeout):
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is not None:
                break
            gevent.sleep(random.random())
    return txn_receipt


def wait_for_block_number(web3, block_number=1, timeout=120):

    with gevent.Timeout(timeout):
        while web3.eth.blockNumber < block_number:
            if isinstance(web3.currentProvider, TestRPCProvider):
                web3._requestManager.request_blocking("evm_mine", [])
                gevent.sleep(0)
            else:
                gevent.sleep(random.random())
    return web3.eth.getBlock(block_number)


def wait_for_unlock(web3, account=None, timeout=120):
    from .accounts import is_account_locked

    if account is None:
        account = web3.eth.coinbase

    with gevent.Timeout(timeout):
        while is_account_locked(web3, account):
            gevent.sleep(random.random())


def wait_for_peers(web3, peer_count=1, timeout=120):
    with gevent.Timeout(timeout):
        while web3.net.peerCount < peer_count:
            gevent.sleep(random.random())


def wait_for_syncing(web3, timeout=120):
    start_block = web3.eth.blockNumber
    with gevent.Timeout(timeout):
        while not web3.eth.syncing and web3.eth.blockNumber == start_block:
            gevent.sleep(random.random())


class Wait(object):
    web3 = None
    timeout = 120

    def __init__(self, web3, timeout=empty):
        self.web3 = web3
        if timeout is not empty:
            self.timeout = timeout

    def for_contract_address(self, txn_hash, timeout=empty):
        txn_receipt = self.for_receipt(txn_hash, timeout=timeout)
        return txn_receipt['contractAddress']

    def for_receipt(self, txn_hash, timeout=empty):
        if timeout is empty:
            timeout = self.timeout

        return wait_for_transaction_receipt(self.web3, txn_hash, timeout=timeout)

    def for_block(self, block_number=empty, timeout=empty):
        kwargs = {}
        if block_number is not empty:
            kwargs['block_number'] = block_number
        if timeout is empty:
            timeout = self.timeout

        return wait_for_block_number(self.web3, timeout=timeout, **kwargs)

    def for_unlock(self, account=empty, timeout=empty):
        kwargs = {}
        if account is not empty:
            kwargs['account'] = account
        if timeout is empty:
            timeout = self.timeout
        return wait_for_unlock(self.web3, timeout=timeout, **kwargs)

    def for_peers(self, peer_count=empty, timeout=empty):
        kwargs = {}
        if peer_count is not empty:
            kwargs['peer_count'] = peer_count
        if timeout is empty:
            timeout = self.timeout
        return wait_for_peers(self.web3, timeout=timeout, **kwargs)

    def for_syncing(self, timeout=empty):
        if timeout is empty:
            timeout = self.timeout
        return wait_for_syncing(self.web3, timeout=timeout)
