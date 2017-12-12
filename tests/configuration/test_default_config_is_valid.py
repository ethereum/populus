from populus import Project


def test_default_configuration_is_valid(project_dir):
    project = Project(project_dir)
    assert project._config_schema is not None
    project.config.validate()
