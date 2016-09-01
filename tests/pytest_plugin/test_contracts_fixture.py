from populus import Project


def test_contracts_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    contracts = request.getfuncargvalue('contracts')

    project = Project()

    assert contracts.Math
    assert len(contracts.Math.code) > 2
    assert len(contracts.Math.code_runtime) > 2
    assert contracts.Math.abi == MATH['abi']
