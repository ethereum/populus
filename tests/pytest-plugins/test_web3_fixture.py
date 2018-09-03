def test_web3_fixture(request, project_dir):
    chain = request.getfixturevalue('chain')
    web3 = request.getfixturevalue('web3')

    assert web3 is chain.web3
