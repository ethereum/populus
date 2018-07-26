def test_web3_fixture(request, project_dir):
    web3 = request.getfixturevalue('web3')
    accounts = request.getfixturevalue('accounts')

    assert web3.eth.accounts == accounts
