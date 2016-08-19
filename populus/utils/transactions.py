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


def is_account_locked(web3, account):
    try:
        web3.eth.sign(account, 'simple-test-data')
    except ValueError as err:
        return 'account is locked' in str(err)
    else:
        return False


def wait_for_unlock(web3, account=None, timeout=0):
    if account is None:
        account = web3.eth.coinbase

    with gevent.Timeout(timeout):
        while is_account_locked(web3, account):
            gevent.sleep(random.random())


def wait_for_peers(web3, peer_count=1, timeout=0):
    with gevent.Timeout(timeout):
        while web3.net.peerCount < peer_count:
            gevent.sleep(random.random())


def wait_for_syncing(web3, timeout=0):
    with gevent.Timeout(timeout):
        while not web3.eth.syncing:
            gevent.sleep(random.random())
