from populus.project import Project


def test_project_dir_defaults_to_cwd(project_dir):
    project = Project()

    assert project.project_dir == project_dir
