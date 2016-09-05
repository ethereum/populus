def is_account_locked(web3, account):
    try:
        web3.eth.sign(account, 'simple-test-data')
    except ValueError as err:
        return 'account is locked' in str(err)
    else:
        return False
