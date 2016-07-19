import gevent


def get_contract_address_from_txn(web3, txn_hash, max_wait=0):
    with gevent.Timeout(max_wait):
        while True:
            txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
            if txn_receipt is None:
                continue
            else:
                break

    return txn_receipt['contractAddress']
