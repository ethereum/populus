def test_base_contract_factories_fixture(request, project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    base_contract_factories = request.getfuncargvalue('base_contract_factories')

    assert 'Math' in base_contract_factories
