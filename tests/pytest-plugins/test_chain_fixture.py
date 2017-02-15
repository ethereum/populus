def test_chain_fixture(request):
    chain = request.getfuncargvalue('chain')
    assert chain.web3.isConnected
