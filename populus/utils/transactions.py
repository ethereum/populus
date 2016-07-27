import gevent


def get_contract_address_from_txn(web3, txn_hash, timeout=0):
    with gevent.Timeout(timeout):
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is None:
                continue
            else:
                break

    return txn_receipt['contractAddress']


def get_block_gas_limit(web3, block_identifier=None):
    if block_identifier is None:
        block_identifier = web3.eth.blockNumber
    block = web3.eth.getBlock(block_identifier)
    return block['gasLimit']
