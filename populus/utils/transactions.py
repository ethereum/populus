import random
import gevent


def wait_for_transaction_receipt(web3, txn_hash, timeout=0):
    with gevent.Timeout(timeout):
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is not None:
                break
            gevent.sleep(random.random())
    return txn_receipt


def wait_for_block_number(web3, block_number=1, timeout=0):
    with gevent.Timeout(timeout):
        while web3.eth.blockNumber < block_number:
            gevent.sleep(random.random())
    return web3.eth.getBlock(block_number)


def get_contract_address_from_txn(web3, txn_hash, timeout=0):
    txn_receipt = wait_for_transaction_receipt(web3, txn_hash, timeout)

    return txn_receipt['contractAddress']


def get_block_gas_limit(web3, block_identifier=None):
    if block_identifier is None:
        block_identifier = web3.eth.blockNumber
    block = web3.eth.getBlock(block_identifier)
    return block['gasLimit']
