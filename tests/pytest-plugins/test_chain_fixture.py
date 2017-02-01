def test_chain_fixture(project_dir, write_project_file, request, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file('migrations/__init__.py')

    project = request.getfuncargvalue('project')

    chain = request.getfuncargvalue('chain')
    assert chain.web3.isConnected
