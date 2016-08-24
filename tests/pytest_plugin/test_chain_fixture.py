def test_chain_fixture(request, project_dir):
    chain = request.getfuncargvalue('chain')

    web3 = chain.web3

    client_name, _, _, _ = web3.version.node.split('/')

    assert client_name == "TestRPC"
