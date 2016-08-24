def test_project_fixture(request, project_dir):
    project = request.getfuncargvalue('project')

    assert project.project_dir == project_dir
