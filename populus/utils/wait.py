import random
import gevent

from web3.providers.tester import (
    TestRPCProvider,
    EthereumTesterProvider,
)

from .empty import empty


def is_tester_web3(web3):
    return isinstance(web3.currentProvider, (TestRPCProvider, EthereumTesterProvider))


def wait_for_transaction_receipt(web3, txn_hash, timeout=120, poll_interval=None):
    with gevent.Timeout(timeout):
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is not None and txn_receipt['blockHash'] is not None:
                break
            if poll_interval is None:
                gevent.sleep(random.random())
            else:
                gevent.sleep(poll_interval)
    return txn_receipt


def wait_for_block_number(web3, block_number=1, timeout=120, poll_interval=None):

    with gevent.Timeout(timeout):
        while web3.eth.blockNumber < block_number:
            if is_tester_web3(web3):
                web3._requestManager.request_blocking("evm_mine", [])
                gevent.sleep(0)
            else:
                if poll_interval is None:
                    gevent.sleep(random.random())
                else:
                    gevent.sleep(poll_interval)
    return web3.eth.getBlock(block_number)


def wait_for_unlock(web3, account=None, timeout=120, poll_interval=None):
    from .accounts import is_account_locked

    if account is None:
        account = web3.eth.coinbase

    with gevent.Timeout(timeout):
        while is_account_locked(web3, account):
            if poll_interval is None:
                gevent.sleep(random.random())
            else:
                gevent.sleep(poll_interval)
    return account


def wait_for_peers(web3, peer_count=1, timeout=120, poll_interval=None):
    with gevent.Timeout(timeout):
        while web3.net.peerCount < peer_count:
            gevent.sleep(random.random())


def wait_for_syncing(web3, timeout=120, poll_interval=None):
    start_block = web3.eth.blockNumber
    with gevent.Timeout(timeout):
        while not web3.eth.syncing and web3.eth.blockNumber == start_block:
            if poll_interval is None:
                gevent.sleep(random.random())
            else:
                gevent.sleep(poll_interval)
    return web3.eth.syncing


class Wait(object):
    web3 = None
    timeout = 120
    poll_interval = None

    def __init__(self, web3, timeout=empty, poll_interval=empty):
        self.web3 = web3
        if timeout is not empty:
            self.timeout = timeout
        if poll_interval is not empty:
            self.poll_interval = poll_interval

    def for_contract_address(self, txn_hash, timeout=empty, poll_interval=empty):
        kwargs = {}
        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        txn_receipt = self.for_receipt(txn_hash, **kwargs)
        return txn_receipt['contractAddress']

    def for_receipt(self, txn_hash, timeout=empty, poll_interval=empty):
        kwargs = {}

        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        return wait_for_transaction_receipt(self.web3, txn_hash, **kwargs)

    def for_block(self, block_number=empty, timeout=empty, poll_interval=empty):
        kwargs = {}

        if block_number is not empty:
            kwargs['block_number'] = block_number
        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        return wait_for_block_number(self.web3, **kwargs)

    def for_unlock(self, account=empty, timeout=empty, poll_interval=empty):
        kwargs = {}

        if account is not empty:
            kwargs['account'] = account
        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        return wait_for_unlock(self.web3, **kwargs)

    def for_peers(self, peer_count=empty, timeout=empty, poll_interval=empty):
        kwargs = {}

        if peer_count is not empty:
            kwargs['peer_count'] = peer_count
        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        return wait_for_peers(self.web3, **kwargs)

    def for_syncing(self, timeout=empty, poll_interval=empty):
        kwargs = {}

        if timeout is not empty:
            kwargs['timeout'] = timeout
        if poll_interval is not empty:
            kwargs['poll_interval'] = poll_interval

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('poll_interval', self.poll_interval)

        return wait_for_syncing(self.web3, **kwargs)
