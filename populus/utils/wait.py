import functools
import random
import time

from web3.providers.tester import (
    EthereumTesterProvider,
    TestRPCProvider,
)


class Timeout(Exception):
    """
    A limited subset of the `gevent.Timeout` context manager.
    """
    seconds = None
    exception = None
    begun_at = None
    is_running = None

    def __init__(self, seconds=None, exception=None, *args, **kwargs):
        self.seconds = seconds
        self.exception = exception

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __str__(self):
        if self.seconds is None:
            return ''
        return "{0} seconds".format(self.seconds)

    @property
    def expire_at(self):
        if self.seconds is None:
            raise ValueError("Timeouts with `seconds == None` do not have an expiration time")
        elif self.begun_at is None:
            raise ValueError("Timeout has not been started")
        return self.begun_at + self.seconds

    def start(self):
        if self.is_running is not None:
            raise ValueError("Timeout has already been started")
        self.begun_at = time.time()
        self.is_running = True

    def check(self):
        if self.is_running is None:
            raise ValueError("Timeout has not been started")
        elif self.is_running is False:
            raise ValueError("Timeout has already been cancelled")
        elif self.seconds is None:
            return
        elif time.time() > self.expire_at:
            self.is_running = False
            if isinstance(self.exception, type):
                raise self.exception(str(self))
            elif isinstance(self.exception, Exception):
                raise self.exception
            else:
                raise self

    def cancel(self):
        self.is_running = False

    def sleep(self, seconds):
        time.sleep(seconds)
        self.check()


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
