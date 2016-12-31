from populus import Project


def test_testrpc_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('testrpc') as chain:
        assert chain.has_registrar is True


def test_tester_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('tester') as chain:
        assert chain.has_registrar is True


def test_temp_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('temp') as chain:
        assert chain.has_registrar is True


def test_geth_chain_has_registrar(project_dir, write_project_file):
    write_project_file('populus.ini', '[chain:local]\nregistrar=faking-it')

    project = Project()

    with project.get_chain('local') as chain:
        assert chain.has_registrar is True
