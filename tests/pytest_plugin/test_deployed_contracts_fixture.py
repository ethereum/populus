def test_deployed_contracts_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    deployed_contracts = request.getfuncargvalue('deployed_contracts')

    math = deployed_contracts.Math
    assert math.address

    assert math.call().add(11, 12) == 23
    assert math.call().multiply7(11) == 77
    assert math.call().return13() == 13
