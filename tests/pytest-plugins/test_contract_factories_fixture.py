from populus import Project


def test_contracts_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    contract_factories = request.getfuncargvalue('contract_factories')

    project = Project()

    assert contract_factories.Math
    assert len(contract_factories.Math.code) > 2
    assert len(contract_factories.Math.code_runtime) > 2
    assert len(contract_factories.Math.abi) == len(MATH['abi'])
