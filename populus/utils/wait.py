import functools
import random

from web3.providers.tester import (
    EthereumTesterProvider,
    TestRPCProvider,
)

from .compat import (
    Timeout,
)


def poll_until(poll_fn, success_fn, timeout, poll_interval_fn):
    with Timeout(timeout) as _timeout:
        while True:
            value = poll_fn()

            if success_fn(value):
                return value

            _timeout.sleep(poll_interval_fn())


def is_tester_web3(web3):
    return isinstance(web3.currentProvider, (TestRPCProvider, EthereumTesterProvider))


def wait_for_transaction_receipt(web3, txn_hash, timeout=120, poll_interval=None):
    return poll_until(
        poll_fn=functools.partial(web3.eth.getTransactionReceipt, txn_hash),
        success_fn=lambda r: r is not None and r['blockHash'] is not None,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )


def wait_for_block_number(web3, block_number=1, timeout=120, poll_interval=None):
    if is_tester_web3(web3):
        if hasattr(web3, 'manager'):
            rm = web3.manager
        else:
            rm = web3._requestManager

        while web3.eth.blockNumber < block_number:
            rm.request_blocking("evm_mine", [])
        return web3.eth.getBlock(block_number)
    return poll_until(
        poll_fn=lambda: web3.eth.blockNumber,
        success_fn=lambda v: v >= block_number,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )


def wait_for_unlock(web3, account=None, timeout=120, poll_interval=None):
    from .accounts import is_account_locked

    if account is None:
        account = web3.eth.coinbase

    return poll_until(
        poll_fn=functools.partial(is_account_locked, web3, account),
        success_fn=lambda v: v,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )


def wait_for_peers(web3, peer_count=1, timeout=120, poll_interval=None):
    return poll_until(
        poll_fn=lambda: web3.net.peerCount,
        success_fn=lambda v: v >= peer_count,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )


def wait_for_syncing(web3, timeout=120, poll_interval=None):
    return poll_until(
        poll_fn=lambda: web3.eth.syncing,
        success_fn=lambda v: v,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )


def wait_for_popen(proc, timeout=5, poll_interval=None):
    return poll_until(
        poll_fn=lambda: proc.poll,
        success_fn=lambda v: v,
        timeout=timeout,
        poll_interval_fn=lambda: poll_interval if poll_interval is not None else random.random(),
    )
