deploy_client_type = 'ethtester'


def test_accounts(accounts):
    from ethereum import tester
    assert len(accounts) == len(tester.accounts)
