def test_web3_fixture(request, project_dir):
    chain = request.getfuncargvalue('chain')
    web3 = request.getfuncargvalue('web3')

    assert web3 is chain.web3
