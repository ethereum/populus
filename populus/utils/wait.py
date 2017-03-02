import random

from web3.providers.tester import (
    EthereumTesterProvider,
    TestRPCProvider,
)

from .compat import (
    Timeout,
)


def is_tester_web3(web3):
    return isinstance(web3.currentProvider, (TestRPCProvider, EthereumTesterProvider))


def wait_for_transaction_receipt(web3, txn_hash, timeout=120, poll_interval=None):
    with Timeout(timeout) as _timeout:
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is not None and txn_receipt['blockHash'] is not None:
                break
            if poll_interval is None:
                _timeout.sleep(random.random())
            else:
                _timeout.sleep(poll_interval)
    return txn_receipt


def wait_for_block_number(web3, block_number=1, timeout=120, poll_interval=None):

    with Timeout(timeout) as _timeout:
        while web3.eth.blockNumber < block_number:
            if is_tester_web3(web3):
                web3._requestManager.request_blocking("evm_mine", [])
                _timeout.sleep(0)
            else:
                if poll_interval is None:
                    _timeout.sleep(random.random())
                else:
                    _timeout.sleep(poll_interval)
    return web3.eth.getBlock(block_number)


def wait_for_unlock(web3, account=None, timeout=120, poll_interval=None):
    from .accounts import is_account_locked

    if account is None:
        account = web3.eth.coinbase

    with Timeout(timeout) as _timeout:
        while is_account_locked(web3, account):
            if poll_interval is None:
                _timeout.sleep(random.random())
            else:
                _timeout.sleep(poll_interval)
    return account


def wait_for_peers(web3, peer_count=1, timeout=120, poll_interval=None):
    with Timeout(timeout) as _timeout:
        while web3.net.peerCount < peer_count:
            _timeout.sleep(random.random())


def wait_for_syncing(web3, timeout=120, poll_interval=None):
    start_block = web3.eth.blockNumber
    with Timeout(timeout) as _timeout:
        while not web3.eth.syncing and web3.eth.blockNumber == start_block:
            if poll_interval is None:
                _timeout.sleep(random.random())
            else:
                _timeout.sleep(poll_interval)
    return web3.eth.syncing
