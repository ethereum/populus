from populus.utils.empty import empty
from populus.utils.wait import (
    wait_for_block_number,
    wait_for_peers,
    wait_for_syncing,
    wait_for_transaction_receipt,
    wait_for_unlock,
)


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
