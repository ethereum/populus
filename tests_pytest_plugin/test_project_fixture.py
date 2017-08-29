from populus.utils.filesystem import is_same_path


def test_project_fixture(request, project):
    request_project = request.getfuncargvalue('project')

    assert is_same_path(
        project.project_root_dir,
        request_project.project_root_dir,
    )
