def test_contracts_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    contracts = request.getfuncargvalue('contracts')

    assert contracts.Math
    assert contracts.Math.code == MATH['code']
    assert contracts.Math.code_runtime == MATH['code_runtime']
    assert contracts.Math.abi == MATH['abi']
