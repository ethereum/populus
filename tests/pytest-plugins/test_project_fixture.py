from populus.utils.filesystem import is_same_path


def test_project_fixture(request, project_dir):
    project = request.getfixturevalue('project')

    assert is_same_path(project.project_dir, project_dir)
