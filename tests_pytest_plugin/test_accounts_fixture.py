def test_web3_fixture(request):
    web3 = request.getfuncargvalue('web3')
    accounts = request.getfuncargvalue('accounts')

    assert web3.eth.accounts == accounts
