def test_chain_fixture(request):
    chain = request.getfixturevalue('chain')
    assert chain.web3.isConnected
