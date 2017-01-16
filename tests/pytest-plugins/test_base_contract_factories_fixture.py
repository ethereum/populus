from populus import Project


def test_base_contract_factories_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    base_contract_factories = request.getfuncargvalue('base_contract_factories')

    project = Project()

    assert base_contract_factories.Math
    assert len(base_contract_factories.Math.code) > 2
    assert len(base_contract_factories.Math.code_runtime) > 2
    assert len(base_contract_factories.Math.abi) == len(MATH['abi'])
