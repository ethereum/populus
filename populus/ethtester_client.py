"""
Large portions of this implementation were influenced or downright copied from
the `eth-testrpc` project by ConsenSys

https://github.com/ConsenSys/eth-testrpc
"""
import time
import Queue
import threading
import uuid


from ethereum import utils as ethereum_utils
from ethereum import tester as t


def strip_0x(value):
    if value and value.startswith('0x'):
        return value[2:]
    return value


def encode_hex(value):
    return "0x" + ethereum_utils.encode_hex(value)


def int_to_hex(value):
    if value == 0:
        return hex(0)
    return ethereum_utils.int_to_hex(value)


def serialize_txn_to_receipt(block, txn, txn_index):
    txn_receipt = block.get_receipt(txn_index)
    origin_gas = block.transaction_list[0].startgas

    if txn.creates is not None:
        contract_addr = encode_hex(txn.creates)
    else:
        contract_addr = None

    return {
        "transactionHash": encode_hex(txn.hash),
        "transactionIndex": int_to_hex(txn_index),
        "blockNumber": int_to_hex(block.number),
        "blockHash": encode_hex(block.hash),
        "cumulativeGasUsed": int_to_hex(origin_gas - txn.startgas + txn_receipt.gas_used),
        "gasUsed": int_to_hex(txn_receipt.gas_used),
        "contractAddress": contract_addr,
        "logs": [
            serialize_log(block, txn, txn_index, log, log_index)
            for log_index, log in enumerate(txn_receipt.logs)
        ],
    }


def serialize_txn(block, txn, txn_index):
    return {
        "hash": encode_hex(txn.hash),
        "nonce": int_to_hex(txn.nonce),
        "blockHash": encode_hex(block.hash),
        "blockNumber": int_to_hex(block.number),
        "transactionIndex": int_to_hex(txn_index),
        "from": encode_hex(txn.sender),
        "to": encode_hex(txn.to),
        "value": int_to_hex(txn.value),
        "gas": int_to_hex(txn.startgas),
        "gasPrice": int_to_hex(txn.gasprice),
        "input": encode_hex(txn.data)
    }


def serialize_log(block, txn, txn_index, log, log_index):
    return {
        "type": "mined",
        "logIndex": int_to_hex(log_index),
        "transactionIndex": int_to_hex(txn_index),
        "transactionHash": encode_hex(txn.hash),
        "blockHash": encode_hex(block.hash),
        "blockNumber": int_to_hex(block.number),
        "address": encode_hex(log.address),
        "data": encode_hex(log.data),
        "topics": [int_to_hex(topic) for topic in log.topics],
    }


def serialize_block(block, full_transactions):
    if full_transactions:
        transactions = [
            serialize_txn(block, txn, txn_index)
            for txn_index, txn in enumerate(block.transaction_list)
        ]
    else:
        transactions = [encode_hex(txn.hash) for txn in block.transaction_list]

    unpadded_logs_bloom = ethereum_utils.int_to_bytes(block.bloom)
    logs_bloom = "\x00" * (256 - len(unpadded_logs_bloom)) + unpadded_logs_bloom

    return {
        "number": int_to_hex(block.number),
        "hash": "0x" + encode_hex(block.hash),
        "parentHash": "0x" + encode_hex(block.prevhash),
        "nonce": "0x" + encode_hex(block.nonce),
        "sha3Uncles": "0x" + encode_hex(block.uncles_hash),
        # TODO logsBloom / padding
        "logsBloom": logs_bloom,
        "transactionsRoot": "0x" + encode_hex(block.tx_list_root),
        "stateRoot": "0x" + encode_hex(block.state_root),
        "miner": "0x" + encode_hex(block.coinbase),
        "difficulty": int_to_hex(block.difficulty),
        # https://github.com/ethereum/pyethereum/issues/266
        # "totalDifficulty": int_to_hex(block.chain_difficulty()),
        "size": int_to_hex(len(ethereum_utils.rlp.encode(block))),
        "extraData": "0x" + encode_hex(block.extra_data),
        "gasLimit": int_to_hex(block.gas_limit),
        "gasUsed": int_to_hex(block.gas_used),
        "timestamp": int_to_hex(block.timestamp),
        "transactions": transactions,
        "uncles": block.uncles
    }


class EthTesterClient(object):
    """
    Stand-in replacement for the rpc client that speaks directly to the
    `ethereum.tester` facilities.
    """
    def __init__(self, async=True, async_timeout=10):
        self.evm = t.state()
        self.evm.block.gas_limit = 3141592
        self.evm.mine()

        self.is_async = async
        self.async_timeout = async_timeout

        if self.is_async:
            self.request_queue = Queue.Queue()
            self.results = {}

            self.request_thread = threading.Thread(target=self.process_requests)
            self.request_thread.daemon = True
            self.request_thread.start()

    def process_requests(self):
        while True:
            id, args, kwargs = self.request_queue.get()
            mine = kwargs.pop('_mine', False)
            try:
                self._send_transaction(*args, **kwargs)
                if mine:
                    self.evm.mine()
                response = self.evm.last_tx.hash
            except Exception as e:
                response = e
                if mine:
                    self.evm.mine()
            self.results[id] = response

    def wait_for_block(self, block_number, max_wait=0):
        while self.evm.block.number < block_number:
            self.evm.mine()
        return self.get_block_by_number(self.evm.block.number)

    def wait_for_transaction(self, txn_hash, max_wait=0):
        return self.get_transaction_receipt(txn_hash)

    def get_max_gas(self):
        return t.gas_limit

    def get_coinbase(self):
        return "0x" + ethereum_utils.encode_hex(self.evm.block.coinbase)

    def get_accounts(self):
        return [
            "0x" + ethereum_utils.encode_hex(addr)
            for addr in t.accounts
        ]

    def get_code(self, address, block_number="latest"):
        block = self._get_block_by_number(block_number)
        return ethereum_utils.encode_hex(block.get_code(strip_0x(address)))

    def _send_transaction(self, _from=None, to=None, gas=None, gas_price=None,
                          value=0, data=''):
        """
        The tester doesn't care about gas so we discard it.
        """
        if _from is None:
            _from = self.get_coinbase()

        _from = strip_0x(_from)

        if len(_from) == 40:
            _from = ethereum_utils.decode_hex(strip_0x(_from))

        sender = t.keys[t.accounts.index(_from)]

        if to is None:
            to = ''

        to = ethereum_utils.decode_hex(strip_0x(to))

        if data is None:
            data = ''

        data = ethereum_utils.decode_hex(strip_0x(data))

        return self.evm.send(sender=sender, to=to, value=value, evmdata=data)

    def send_transaction(self, *args, **kwargs):
        if self.is_async:
            kwargs['_mine'] = True
            request_id = uuid.uuid4()
            self.request_queue.put((request_id, args, kwargs))
            start = time.time()
            while time.time() - start < self.async_timeout:
                if request_id in self.results:
                    result = self.results.pop(request_id)
                    if isinstance(result, Exception):
                        raise result
                    return result
            raise ValueError("Timeout waiting for {0}".format(request_id))
        else:
            self._send_transaction(*args, **kwargs)
            self.evm.mine()
            return self.evm.last_tx.hash

    def _get_transaction_by_hash(self, txn_hash):
        txn_hash = strip_0x(txn_hash)
        if len(txn_hash) == 64:
            txn_hash = ethereum_utils.decode_hex(txn_hash)
        for block in reversed(self.evm.blocks):
            txn_hashes = block.get_transaction_hashes()

            if txn_hash in txn_hashes:
                txn_index = txn_hashes.index(txn_hash)
                txn = block.transaction_list[txn_index]
                break
        else:
            raise ValueError("Transaction not found")
        return block, txn, txn_index

    def get_transaction_receipt(self, txn_hash):
        block, txn, txn_index = self._get_transaction_by_hash(txn_hash)

        return serialize_txn_to_receipt(block, txn, txn_index)

    def _get_block_by_number(self, block_number="latest"):
        if block_number == "latest":
            return self.evm.block
        elif block_number == "earliest":
            return self.evm.blocks[0]
        elif block_number == "pending":
            raise ValueError("Fetching 'pending' block is unsupported")
        else:
            if str(block_number).startswith("0x"):
                block_number = int(block_number, 16)
            if block_number >= len(self.evm.blocks):
                raise ValueError("Invalid block number")
            return self.evm.blocks[block_number]

    def get_block_by_number(self, block_number, full_transactions=True):
        block = self._get_block_by_number(block_number)

        return serialize_block(block, full_transactions)

    def _get_block_by_hash(self, block_hash):
        if len(block_hash) > 32:
            block_hash = ethereum_utils.decode_hex(strip_0x(block_hash))
        for block in self.evm.blocks:
            if block.hash == block_hash:
                return block
        else:
            raise ValueError("Could not find block for provided hash")

    def get_block_by_hash(self, block_hash, full_transactions=True):
        block = self._get_block_by_hash(block_hash)

        return serialize_block(block, full_transactions)

    def get_block_number(self):
        return self.evm.block.number

    def get_gas_price(self):
        return t.gas_price

    def get_balance(self, address, block="latest"):
        _block = self._get_block_by_number(block)
        return _block.get_balance(strip_0x(address))

    def call(self, *args, **kwargs):
        if len(args) >= 7 and args[6] != "latest":
            raise ValueError("Using call on any block other than latest is unsupported")
        if kwargs.get('block', 'latest') != "latest":
            raise ValueError("Using call on any block other than latest is unsupported")
        snapshot = self.evm.snapshot()
        r = self._send_transaction(*args, **kwargs)
        self.evm.revert(snapshot)
        # Stop-gap solution for bug with a transaction that immediately follows
        # a call.
        self.evm.mine()
        return encode_hex(r)

    def get_transaction_by_hash(self, txn_hash):
        block, txn, txn_index = self._get_transaction_by_hash(txn_hash)
        return serialize_txn(block, txn, txn_index)
