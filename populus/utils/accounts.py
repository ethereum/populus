from eth_utils import (
    is_same_address,
)

from web3.providers.tester import (
    EthereumTesterProvider,
    TestRPCProvider,
)


def is_account_locked(web3, account):
    if isinstance(web3.currentProvider, (EthereumTesterProvider, TestRPCProvider)):
        return not any((is_same_address(account, a) for a in web3.eth.accounts[:10]))
    try:
        web3.eth.sign(account, 'simple-test-data')
    except ValueError as err:
        return 'account is locked' in str(err)
    else:
        return False
